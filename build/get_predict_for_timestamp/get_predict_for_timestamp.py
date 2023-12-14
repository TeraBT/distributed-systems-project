from datetime import datetime

# flag to indicate if workflow is in debugging mode
DEBUG = True


def handler(event, context):
    """Creates a POSIX timestamp to define the time for which predictions/info updates are desired.
    For developing/debugging the workflow this value should be hardcoded considering the test dataset.
    For production this value should be generated from a system clock.
    """

    predict_for = int(datetime.now().timestamp())

    if DEBUG:
        predict_for = 0  # hardcoded value for debugging goes here

    return predict_for
