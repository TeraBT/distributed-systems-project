def handler(event, context):
    """Uses car counts for specific times to predict the car count for another time using linear
    regression or any other reasonably simple prediction model.

    Return to workflow:
    - type: int
    - value: the number of cars predicted for the given time
    """
    # input from workflow
    # the POSIX timestamp of the time for which the predict shall be made
    predict_for: int = event["predictFor"]
    # a dictionary of car counts for specific times, where the key is the time (POSIX timestamp) and the value is the car count
    car_count: dict[int, int] = {int(k): v for k, v in event["carCount"].items()}

    # output to workflow
    car_count_preediction = 10  # dummy value for workflow testing - TODO: remove
    return car_count_preediction
