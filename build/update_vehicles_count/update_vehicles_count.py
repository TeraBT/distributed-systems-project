import boto3
import os

# the central DynamoDB table
table = boto3.resource("dynamodb").Table(os.environ["DB_NAME"])


def handler(event, context):
    """Takes car count prediction and emergency vehicle count for a specific camera
    and a specific prediction time and stores the result in the central DynamoDB table."""
    # input from workflow
    # the POSIX timestamp of the time for which predictions have been made and vehicle counts have been checked
    predict_for: int = event["predictFor"]
    # the ID of the camera for which predictions have been made and vehicle counts have been checked
    camera_id: str = event["cameraId"]
    # the prediction of the car count, based on historic images
    car_count_prediction: int = event["counts"]["carCountPrediction"]
    # the emergency vehicle count, based on the latest historic image
    emergency_vehicle_count: int = event["counts"]["emergencyVehicleCount"]

    # no output to workflow required - result stored in DynamoDB directly
    return {}
