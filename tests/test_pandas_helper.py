import pytest
import pandas as pd

from utils import PandasHelper as h


@pytest.fixture
def A():
    return pd.DataFrame(
        [
            (0, 0),
            (1, 1),
            (2, 4),
            (3, 9),
        ]
    )


@pytest.fixture
def B():
    return pd.DataFrame(
        [
            (0, 0),
            (2, 4),
        ]
    )


@pytest.fixture
def B2():
    return pd.DataFrame(
        [
            (0, 99),
            (2, 99),
        ]
    )


def test_diff_from_same(A, B):
    """Subtracting a dataframe from itself should result in an empty df"""
    assert h.diff(A, A).empty
    assert h.diff(B, B).empty


def test_diff_subtracting_nonconflicting_rows(A, B):
    """The two rows that match perfectly should be removed from result"""
    result = h.diff(A, B)
    expected = pd.DataFrame(
        [
            (1, 1),
            (3, 9),
        ]
    )
    assert result.equals(expected)


def test_diff_subtracting_conflicting_rows(A, B2):
    """Since no row in B matches perfectly, the result should be A unmodified"""
    result = h.diff(A, B2)
    expected = A
    assert result.equals(expected)


def test_diff_subtracting_conflicting_rows_but_using_id_rows(A, B2):
    """Since now matching on B[0], only the first column should be used for matching."""
    result = h.diff(A, B2[0])
    expected = pd.DataFrame(
        [
            (1, 1),
            (3, 9),
        ]
    )
    assert result.equals(expected)


def test_conflict_on_nonconflicting_rows(A, B):
    """Since there is no conflict, should be empty"""
    result = h.conflict(A, B, [0])
    assert result.empty


def test_conflict_on_conflicting_rows(A, B2):
    """Returns the two sets of two rows that are in conflict"""
    result = h.conflict(A, B2, [0])
    expected = pd.DataFrame(
        [
            (0, 0, "left"),
            (2, 4, "left"),
            (0, 99, "right"),
            (2, 99, "right"),
        ],
        index=[0, 2, 0, 1],
        columns=[0, 1, "_merge"],
    )
    assert result.equals(expected)
