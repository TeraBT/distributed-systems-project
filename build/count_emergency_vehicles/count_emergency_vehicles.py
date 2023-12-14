def handler(event: dict, context):
    """Counts emergency vehicles in the latest image of an image series by using Rekognition.

    Return value to workflow:
    - type: integer
    - value: the number of emergency vehicles in the latest image
    """
    # input from workflow
    # dictionary with image creation times (POSIX timestamps) as keys and the keys of the images within the bucket
    image_uris: dict[int, str] = {int(k): v for k, v in event.items()}

    # output to workflow
    emergency_vehicle_count = 2  # dummy value for workflow testing - TODO: remove
    return emergency_vehicle_count
