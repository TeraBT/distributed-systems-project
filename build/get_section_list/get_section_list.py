import boto3
import os
import logging

from typing import Tuple, Optional

from boto3.dynamodb.conditions import Key

# setup logging
logging.getLogger().setLevel(logging.INFO)

# the central DynamoDB table
table = boto3.resource("dynamodb").Table(os.environ["DB_NAME"])


def get_section_ids_from_table(
    last_evaluated_key: Optional[dict] = None,
) -> Tuple[Optional[dict], list[str]]:
    """Queries the table and retrieves all section IDs. If more IDs are in the table than can be returned
    with a single query, the last evaluated key will be returned. This can then be re-used in the next
    query.

    :param last_evaluated_key: The key of the last evaluated key on a previous request, defaults to None
    :raises e: If something went wrong while querying
    :return: The last evaluated key (if present) and a list of section IDs
    """

    # query table
    optional_params = {"ExclusiveStartKey": last_evaluated_key} if last_evaluated_key else {}
    try:
        response = table.query(
            KeyConditionExpression=(Key("PK").eq("baseEntity") & Key("SK").begins_with("section#")),
            Select="SPECIFIC_ATTRIBUTES",
            ProjectionExpression="SK",
            **optional_params,
        )
    except Exception as e:
        logging.error(f"Error querying DynamoDB: {e}")
        raise e

    # get section IDs
    items = response["Items"]
    section_ids = [item["SK"].replace("section#", "", 1) for item in items]

    # check if there are more results
    if "LastEvaluatedKey" in response:
        last_evaluated_key = response["LastEvaluatedKey"]
    else:
        last_evaluated_key = None

    return last_evaluated_key, section_ids


def handler(event, context):
    """Gets a list of all available sections and returns their IDs.

    Return value to workflow:
    - type: list
    - values: the IDs of all sections in the system
    """
    # no input from workflow required

    # get all sectionIDs from DynamoDB
    section_ids = []
    first_request_done = False
    last_evaluated_key = None
    while first_request_done == False or last_evaluated_key is not None:
        first_request_done = True
        last_evaluated_key, section_ids_batch = get_section_ids_from_table(last_evaluated_key)
        section_ids.extend(section_ids_batch)

    # output to workflow
    return section_ids
