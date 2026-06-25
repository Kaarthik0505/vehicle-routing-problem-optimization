import pandas as pd
from main import validate_input

def test_valid_input():
    data = {
        "order_id": [1, 2],
        "lat": [13.05, 13.06],
        "lon": [80.25, 80.26],
        "demand": [10, 15],
        "start_time": [480, 500],
        "end_time": [600, 650]
    }

    df = pd.DataFrame(data)

    validate_input(df, [50, 50], 2)  # should not raise error


def test_invalid_latitude():
    data = {
        "order_id": [1],
        "lat": [200],  # invalid
        "lon": [80.25],
        "demand": [10],
        "start_time": [480],
        "end_time": [600]
    }

    df = pd.DataFrame(data)

    try:
        validate_input(df, [50], 1)
        assert False
    except ValueError:
        assert True