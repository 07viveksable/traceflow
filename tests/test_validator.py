import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "app")
)

import sys
from pathlib import Path

import pytest


sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "app")
)

from validator import validate_data


def test_valid_data():

    data = [
        {
            "id": "1",
            "name": "Vivek",
            "city": "Pune",
            "product": "Laptop",
            "amount": "55000",
            "status": "Completed"
        }
    ]

    assert validate_data(data) is True


def test_negative_amount():

    data = [
        {
            "id": "1",
            "name": "Vivek",
            "city": "Pune",
            "product": "Laptop",
            "amount": "-5000",
            "status": "Completed"
        }
    ]

    with pytest.raises(ValueError):
        validate_data(data)