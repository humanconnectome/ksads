import pandas as pd


def strip_special_chars(df):
    return df.apply(
        lambda col: col.astype(str)
        .str.replace("’", "'")
        .str.replace("‘", "'")
        .str.replace("“", '"')
        .str.replace("”", '"')
        if col.dtype == "O"
        else col
    )


def to_numeric(column):
    # if date, don't convert
    if column.dtype == "<M8[ns]":
        return column
    try:
        n = pd.to_numeric(column)
        if n.dtype == float and (n % 1 == 0).all():
            n = n.astype(int)
        return n
    except ValueError:
        return column
