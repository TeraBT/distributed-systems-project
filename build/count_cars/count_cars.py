import os

# the name of the bucket where the images are stored
bucket_name = os.environ["BUCKET_NAME"]


def handler(event: dict, context):
    """Counts cars in a given list of images by using Rekognition.

    Return value to workflow:
    - type: dictionary
    - keys: POSIX timestamps as integers
    - values: the number of cars in each image as an integer
    """
    # input from workflow
    # dictionary with image creation times (POSIX timestamps) as keys and the keys of the images within the bucket
    image_uris: dict[int, str] = {int(k): v for k, v in event.items()}

    # output to workflow
    car_counts = {1: 5, 2: 10}  # dummy value for workflow testing - TODO: remove
    return car_counts
