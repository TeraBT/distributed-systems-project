import os
import boto3
import logging

from typing import Tuple
from statistics import mean

from boto3.dynamodb.types import TypeDeserializer

# setup logging
logging.getLogger().setLevel(logging.INFO)

# DynamoDB client (as BatchGetItem method is required, that is not available on Table resource)
table_name = os.environ["DB_NAME"]
dynamodb = boto3.client("dynamodb")

# constants
# number of cameras with the highest load to consider for overall traffic load calculation
NUM_CAMERAS_TO_CONSIDER = 3
# min. number of detected emergency vehicles (in at least one image) to consider emergency vehicles to be active
MIN_NUM_EMERGENCY_VEHICLES = 1


def get_street_data(street_id: str) -> Tuple[list[str], str, int, float]:
    """Retrieves the data for a given street from the DynamoDB table.

    :param street_id: The ID of the street to retrieve data for.
    :raises e: If something went wrong while querying
    :return: A tuple containing the following values:
    - list of camera IDs
    - station ID
    - maximum traffic capacity
    - air quality limit
    """

    # query table
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={"PK": {"S": "baseEntity"}, "SK": {"S": f"street#{street_id}"}},
            ProjectionExpression="cameras, station, trafficCapacity, airQualityLimit",
        )
    except Exception as e:
        logging.error(f"Error while querying table: {e}")
        raise e

    # get data
    item = response["Item"]
    item = {k: TypeDeserializer().deserialize(v) for k, v in item.items()}

    # extract values
    cameras = item["cameras"]
    station = item["station"]
    traffic_capacity = int(item["trafficCapacity"])
    air_quality_limit = float(item["airQualityLimit"])

    return cameras, station, traffic_capacity, air_quality_limit


def get_car_counts(
    camera_ids: list[str], predict_for: int
) -> Tuple[dict[str, int], dict[str, int]]:
    """Retrieves the car count prediction and the emergency vehicle count for the specified time

    :param camera_ids: A list of camera IDs for which data shall be retrieved
    :param predict_for: The time for which data shall be retrieved
    :raises e: If something went wrong while querying
    :return: A tuple containing two dictionaries:
    - camera IDs as keys and car count predictions as values
    - camera IDs as keys and emergency vehicle counts as values
    """

    # query table
    try:
        response = dynamodb.batch_get_item(
            RequestItems={
                table_name: {
                    "Keys": [
                        {
                            "PK": {"S": f"camera#{camera_id}"},
                            "SK": {"S": f"trafficCount#{predict_for}"},
                        }
                        for camera_id in camera_ids
                    ],
                    "ProjectionExpression": "PK, carCountPrediction, emergencyVehicleCount",
                    "ConsistentRead": True,
                }
            }
        )
    except Exception as e:
        logging.error(f"Error while querying table: {e}")
        raise e

    # get data and deserialize
    data = response["Responses"][table_name]
    data = [{k: TypeDeserializer().deserialize(v) for k, v in d.items()} for d in data]

    # create dictionaries to return
    car_count_predictions = {
        d["PK"].replace("camera#", "", 1): int(d["carCountPrediction"]) for d in data
    }
    emergency_vehicle_counts = {
        d["PK"].replace("camera#", "", 1): int(d["emergencyVehicleCount"]) for d in data
    }

    return car_count_predictions, emergency_vehicle_counts


def get_air_quality_prediction(station_id: str, predict_for: int) -> float:
    """Retrieves the air quality prediction for the specified time

    :param station_id: The ID of the station for which data shall be retrieved
    :param predict_for: The time for which data shall be retrieved
    :raises e: If something went wrong while querying
    :return: The air quality prediction
    """

    # query table
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={"PK": {"S": f"station#{station_id}"}, "SK": {"S": f"prediction#{predict_for}"}},
            ProjectionExpression="airQuality",
            ConsistentRead=True,
        )
    except Exception as e:
        logging.error(f"Error while querying table: {e}")
        raise e

    # get data and deserialize
    item = response["Item"]
    item = {k: TypeDeserializer().deserialize(v) for k, v in item.items()}

    # extract value
    air_quality_prediction = float(item["airQuality"])

    return air_quality_prediction


def calculate_traffic_load(traffic_capacity: int, car_count_predictions: dict[str, int]) -> float:
    """Calculates the traffic load of a street

    :param traffic_capacity: The maximum traffic capacity of the street
    :param car_count_predictions: The predictions for the car counts for cameras covering the street
    :return: The traffic load as percentage of maximum capacity
    """

    # calculate relative loads for each camera and sort from highest to lowest
    traffic_loads = sorted(
        [
            car_count_prediction / traffic_capacity if traffic_capacity > 0.0 else 1.0
            for car_count_prediction in car_count_predictions.values()
        ],
        reverse=True,
    )

    # calculate overall traffic load from certain number of cameras with highest load
    if len(traffic_loads):
        traffic_load = mean(traffic_loads[:NUM_CAMERAS_TO_CONSIDER])
    else:
        traffic_load = 0.0

    return traffic_load


def check_emergency_vehicles_active(emergency_vehicle_counts: dict[str, int]) -> bool:
    """Checks if there are any active emergency vehicles

    :param emergency_vehicle_counts: The counts for the number of detected emergency vehicles for cameras covering the street
    :return: True if there are any active emergency vehicles, False otherwise
    """

    # check if any of the emergency vehicle counts is greater than 0
    return any(
        emergency_vehicle_count >= MIN_NUM_EMERGENCY_VEHICLES
        for emergency_vehicle_count in emergency_vehicle_counts.values()
    )


def calculate_air_quality_load(air_quality_limit: float, air_quality_prediction: float) -> float:
    """Calculates the air quality load of a street

    :param air_quality_limit: The air quality limit of the street
    :param air_quality_prediction: The air quality prediction for the station covering the street
    :return: The air quality load as percentage of limit
    """

    # calculate relative load
    if air_quality_limit > 0.0:
        air_quality_load = air_quality_prediction / air_quality_limit
    else:
        air_quality_load = 1.0

    return air_quality_load


def put_info(
    street_id: str,
    predict_for: int,
    traffic_load: float,
    emergency_vehicles_active: bool,
    air_quality_load: float,
):
    """Stores the calculated information for the given street and given prediction time in the DynamoDB table

    :param street_id: The ID of the street for which the information shall be stored in DynamoDB
    :param predict_for: The prediction time for which the information shall be stored in DynamoDB
    :param traffic_load: The calculated traffic load as percentage of maximum capacity
    :param emergency_vehicles_active: True if there are any active emergency vehicles, False otherwise
    :param air_quality_load: The calculated air quality load as percentage of limit
    :raises e: If something went wrong while storing data in the table
    """

    # put info in DynamoDB
    try:
        dynamodb.put_item(
            TableName=table_name,
            Item={
                "PK": {"S": f"street#{street_id}"},
                "SK": {"S": f"info#{predict_for}"},
                "trafficLoad": {"N": str(traffic_load)},
                "emergencyVehiclesActive": {"BOOL": emergency_vehicles_active},
                "airQualityLoad": {"N": str(air_quality_load)},
            },
        )
    except Exception as e:
        logging.error(f"Error while putting info in table: {e}")
        raise e


def handler(event, context):
    """Determines if limits for a given street are currently being exceeded, e.g.:
    - current traffic load as percentage of maximum capacity
    - active emergency vehicles (true/false)

    Input data is retrieved from the DynamoDB table:
    - Traffic prediction/analysis for all cameras on the street
    - Air quality prediction for the station covering the street

    The result is stored in DynamoDB directly.
    """
    # input from workflow
    # the POSIX timestamp of the time for which the limits shall be checked
    predict_for: int = event["predictFor"]
    # the ID of the street for which the limits shall be checked
    street_id: str = event["streetId"]

    # get data for the given street
    cameras, station, traffic_capacity, air_quality_limit = get_street_data(street_id)

    # get car count predictions and emergency vehicle counts for cameras covering the street
    car_count_predictions, emergency_vehicle_counts = get_car_counts(cameras, predict_for)

    # get air quality prediction for the station covering the street
    air_quality_prediction = get_air_quality_prediction(station, predict_for)

    # calculate limits
    traffic_load = calculate_traffic_load(traffic_capacity, car_count_predictions)
    emergency_vehicles_active = check_emergency_vehicles_active(emergency_vehicle_counts)
    air_quality_load = calculate_air_quality_load(air_quality_limit, air_quality_prediction)

    # store calculated info in DynamoDB
    put_info(street_id, predict_for, traffic_load, emergency_vehicles_active, air_quality_load)

    # no output to workflow required - result stored in DynamoDB directly
    return {}
