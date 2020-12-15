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


def escape_value(x):
    if isinstance(x, pd.Timestamp):
        return f'"{str(x)}"'
    elif pd.isna(x):
        return "None"
    elif type(x) is str:
        if "\n" in x:
            return f'"""{x}"""'
        else:
            escaped = x.replace('"', r"\"")
            return f'"{escaped}"'
    else:
        return x


def isna(x):
    return pd.isna(x) or x == "nan"


def convert_nan(df):
    return df.apply(lambda col: col.replace("nan", pd.NA) if col.dtype == "O" else col)


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


def synchronize_dtypes(df1, df2):
    for name, a in df1.items():
        if name in df2.columns:
            b = df2[name]
            ad, bd = a.dtype, b.dtype

            # nothing to do
            if ad == bd:
                continue

            # if one is empty, use other
            elif a.isna().all():
                dtype = b.dtype
            elif b.isna().all():
                dtype = a.dtype

            else:
                dtype = a.dtype

            df2[name] = df2[name].astype(dtype)
            df1[name] = df1[name].astype(dtype)
