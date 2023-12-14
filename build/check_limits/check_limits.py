import os
import boto3

# the central DynamoDB table
table = boto3.resource("dynamodb").Table(os.environ["DB_NAME"])


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

    # no output to workflow required - result stored in DynamoDB directly
    return {}
