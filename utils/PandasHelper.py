from IPython.core.display import display, HTML
from pandas import DataFrame, Series


def _subset_to_columns_in_common(a, b):
    columns_in_common = a.columns.intersection(b.columns)
    a = a[columns_in_common]
    b = b[columns_in_common]
    return a, b


def diff(df1, df2):
    if isinstance(df2, Series):
        b = df2.to_frame()
    else:
        b = df2

    a, b = _subset_to_columns_in_common(df1, b)

    indicator = "_merge"
    f = a.merge(b, how="left", indicator=indicator)
    f = f[f[indicator] == "left_only"]
    f = f.drop(columns=indicator)

    result = df1.merge(f, "right").sort_values(f.columns.to_list())
    result.drop_duplicates(inplace=True)

    return result


def conflict(
    left, right, intersect_on, sources=("left", "right"), indicator_name="_merge"
):
    left[indicator_name], right[indicator_name] = sources
    c = left.append(right, sort=False)

    # drop rows with unique identifier columns
    c = c[c.duplicated(subset=intersect_on, keep=False)]

    c.drop_duplicates(subset=c.columns[:-1], keep=False, inplace=True)
    return c


def series_is_equal(series):
    return series.duplicated(keep=False).all()


def unequal_columns(df):
    """Find the name of the columns that are unequal"""
    unequal = [
        colname for colname, value in df.iteritems() if not series_is_equal(value)
    ]
    return unequal


def showbox(message, heading=None, type="success"):
    box = '<div class="alert alert-%s" role="alert">' % type
    if heading:
        box += '<h4 class="alert-heading">%s</h4>' % heading
    box += "<p>%s</p></div>" % message
    return display(HTML(box))


def showdataframe(df):
    if not df.empty:
        print("Size: r%s x c%s" % df.shape)
        display(df[:3])


def asInt(dfs, *columns):
    if isinstance(dfs, DataFrame):
        dfs = [dfs]
    for df in dfs:
        for column in columns:
            df[column] = df[column].astype(float).astype("Int64")
