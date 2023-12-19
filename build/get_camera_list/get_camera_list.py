import boto3
import os
import logging

from typing import Tuple, Optional

from boto3.dynamodb.conditions import Key

# setup logging
logging.getLogger().setLevel(logging.INFO)

# the central DynamoDB table
table = boto3.resource("dynamodb").Table(os.environ["DB_NAME"])


def get_camera_ids_from_table(
    last_evaluated_key: Optional[dict] = None,
) -> Tuple[Optional[dict], list[str]]:
    """Queries the table and retrieves all camera IDs. If more IDs are in the table than can be returned
    with a single query, the last evaluated key will be returned. This can then be re-used in the next
    query.

    :param last_evaluated_key: The key of the last evaluated key on a previous request, defaults to None
    :raises e: If something went wrong while querying
    :return: The last evaluated key (if present) and a list of camera IDs
    """

    # query table
    optional_params = {"ExclusiveStartKey": last_evaluated_key} if last_evaluated_key else {}
    try:
        response = table.query(
            KeyConditionExpression=(Key("PK").eq("baseEntity") & Key("SK").begins_with("camera#")),
            Select="SPECIFIC_ATTRIBUTES",
            ProjectionExpression="SK",
            **optional_params,
        )
    except Exception as e:
        logging.error(f"Error querying DynamoDB: {e}")
        raise e

    # get camera IDs
    items = response["Items"]
    camera_ids = [item["SK"].replace("camera#", "", 1) for item in items]

    # check if there are more results
    if "LastEvaluatedKey" in response:
        last_evaluated_key = response["LastEvaluatedKey"]
    else:
        last_evaluated_key = None

    return last_evaluated_key, camera_ids


def handler(event, context):
    """Gets a list of all available cameras and returns their IDs.

    Return value to workflow:
    - type: list
    - values: the IDs of all cameras in the system
    """
    # no input from workflow required

    # get all camera IDs from DynamoDB
    camera_ids = []
    first_request_done = False
    last_evaluated_key = None
    while first_request_done == False or last_evaluated_key is not None:
        first_request_done = True
        last_evaluated_key, camera_ids_batch = get_camera_ids_from_table(last_evaluated_key)
        camera_ids.extend(camera_ids_batch)

    # output to workflow
    return camera_ids
