import boto3
import os

# the central DynamoDB table
table = boto3.resource("dynamodb").Table(os.environ["DB_NAME"])


def handler(event, context):
    """Retrieves measurements for a specific station from the DynamoDB table
    and makes a prediction for a specified time using linear regression or any
    other suitably simple model.
    No measurements older than a defined amount of time should be considered.
    The prediction is stored in the DynamoDB table again.
    """
    # input from workflow
    # the POSIX timestamp of the time for which an air quality prediction shall be made
    predict_for: int = event["predictFor"]
    # the ID of the station for which the prediction shall be made
    station_id: str = event["stationId"]

    # no output to workflow - result stored in DynamoDB directly
    return {}
