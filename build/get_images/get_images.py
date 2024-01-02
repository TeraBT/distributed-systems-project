import boto3
import os
import logging

from typing import Tuple, Optional

from boto3.dynamodb.conditions import Key

# setup logging
logging.getLogger().setLevel(logging.INFO)

# the central DynamoDB table
table = boto3.resource("dynamodb").Table(os.environ["DB_NAME"])

# constants
MAX_IMAGE_AGE = 7200  # 2h


def get_images_from_table(camera_id: str, earliest_time: int) -> dict[int, str]:
    """Queries the table and retrieves all image URIS for a specific camera as well as the
    times at which they have been taken.

    :param camera_id: The ID of the camera for which images shall be returned
    :param earliest_time: Consider no images older than the given time (use POSIX timestamp)
    :raises e: If something went wrong while querying
    :return: A dictionary with the times at which the images have been taken as keys and the
    image URIs as values.
    """

    # query table
    try:
        response = table.query(
            KeyConditionExpression=(
                Key("PK").eq(f"camera#{camera_id}") & Key("SK").gt(f"image#{earliest_time}")
            ),
            Select="SPECIFIC_ATTRIBUTES",
            ProjectionExpression="SK, URI",
            ScanIndexForward=False,  # to guarantee that newer images are retrieved, in unexpected case pagination takes place
        )
    except Exception as e:
        logging.error(f"Error while querying DynamoDB: {e}")
        raise e

    # get image timestamps and URIs
    items = response["Items"]
    image_uris = {int(item["SK"].replace("image#", "", 1)): item["URI"] for item in items}

    return image_uris


def handler(event, context):
    """Gets all image URIs for a given camera considering the desired time of prediction.
    No images older than a defined amount of time should be considered.
    Image URIs are stored in the DynamoDB table.

    Return value to workflow:
    - type: dictionary
    - keys: POSIX timestamps as integers
    - values: the key under which the image is available within the bucket
    """
    # input from workflow
    # the ID of the camera for which the image URIs shall be retrieved
    camera_id: str = event["cameraId"]
    # the POSIX timestamp of the time for which the image URIs shall be retrieved
    # more specific: the time on which the timerange from which images shall be considered
    predict_for: int = event["predictFor"]

    # determine earliest time at which picture might have been taken to still be considered
    earliest_time = predict_for - MAX_IMAGE_AGE

    # query DynamoDB
    # no need to consider pagination as max. returned result size is 1MB which will be
    # more than sufficient to just return URIs
    image_uris = get_images_from_table(camera_id, earliest_time)

    # output to workflow
    return image_uris
