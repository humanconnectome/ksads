from utils import utils
import pandas as pd
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
