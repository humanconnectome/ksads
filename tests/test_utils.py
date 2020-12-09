from utils import utils
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pytest


def test_strip_special_chars():
    input_ = pd.DataFrame(
        [
            ["He said “Hi”.", "Blah", 1, True],
            ["‘", "He can’t", 2, False],
        ]
    )
    expected = pd.DataFrame(
        [
            ['He said "Hi".', "Blah", 1, True],
            ["'", "He can't", 2, False],
        ]
    )
    actual = utils.strip_special_chars(input_)
    assert actual.equals(expected)


def test_to_numeric_float():
    input_ = pd.Series(["1.0", "2", 3.0, ""])
    actual = utils.to_numeric(input_)
    expected = pd.Series([1, 2, 3, None], dtype=float)

    assert input_.dtype == "O"
    assert actual.dtype == float
    assert actual.equals(expected)


def test_to_numeric_str():
    input_ = pd.Series(["1.0", "2", 3.0, "Blah"])
    actual = utils.to_numeric(input_)
    expected = pd.Series(["1.0", "2", 3.0, "Blah"])

    assert input_.dtype == "O"
    assert actual.dtype == "O"
    assert actual.equals(expected)


def test_to_numeric_multiple_columns():
    input_ = pd.DataFrame([[0, 1, 2], [2.0, 2.0, ""]])
    actual = input_.apply(utils.to_numeric)
    expected_dtypes = [int, int, float]

    assert (actual.dtypes == expected_dtypes).all()


def test_to_numeric_multiple_date_types():
    input_ = pd.DataFrame(
        [
            pd.to_datetime(["2020-02-01", "2020-02-01"]),
            pd.to_datetime(["2020-02-01", "2020-02-01 01:25:44 PM"]),
        ]
    )
    actual = input_.apply(utils.to_numeric)

    assert input_.dtypes.map(is_datetime).all()
    assert actual.dtypes.map(is_datetime).all()
