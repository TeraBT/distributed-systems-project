import boto3
import os

# the central DynamoDB table
table = boto3.resource("dynamodb").Table(os.environ["DB_NAME"])


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

    # output to workflow
    image_uris = {1: "img1_uri", 2: "img2_uri"}  # dummy value for workflow testing - TODO: remove
    return image_uris
