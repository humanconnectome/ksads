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
