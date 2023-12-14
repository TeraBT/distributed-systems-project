import boto3
import os

# the central DynamoDB table
table = boto3.resource("dynamodb").Table(os.environ["DB_NAME"])


def handler(event, context):
    """Gets a list of all available sections and returns their IDs.
    Section IDs are stored in the DynamoDB table and should be retrieved from
    the relations defined there.

    Return value to workflow:
    - type: list
    - values: the IDs of all sections in the system
    """
    # no input from workflow required

    # output to workflow
    section_ids = ["section_1", "section_2"]  # dummy value for workflow testing - TODO: remove
    return section_ids
