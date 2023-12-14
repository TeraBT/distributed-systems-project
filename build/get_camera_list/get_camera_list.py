import boto3
import os

# the central DynamoDB table
table = boto3.resource("dynamodb").Table(os.environ["DB_NAME"])


def handler(event, context):
    """Gets a list of all available cameras and returns their IDs.
    Camera IDs are stored in the DynamoDB table and should be retrieved from
    the relations defined there.

    Return value to workflow:
    - type: list
    - values: the IDs of all cameras in the system
    """
    # no input from workflow required

    # output to workflow
    camera_ids = ["camera_1", "camera_2"]  # dummy value for workflow testing - TODO: remove
    return camera_ids
