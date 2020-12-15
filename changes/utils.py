import pandas as pd
from pandas.core.dtypes.common import is_datetime64_any_dtype as is_datetime

from utils.utils import isna


def block(df, index, reason):
    print(f"Blocking new row {index}, reason: {reason}")
    df.drop(index, inplace=True)


def modify(df, index, column, old_value, new_value):
    col = df[column]
    if is_datetime(col):
        old_value = pd.Timestamp(old_value)
        new_value = pd.Timestamp(new_value)

    if isna(old_value):
        assert isna(df.loc[index, column])
    else:
        assert df.loc[index, column] == old_value, (
        "Fresh data contains unexpected modification.", "Expected: ", old_value, "Actual: ", df.loc[index, column])
    df.loc[index, column] = new_value