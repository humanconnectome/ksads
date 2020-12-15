from changes.utils import block, modify


def execute(df):
    pass
    # block practice rows
    block(df, 19100, "Practice001")
    block(df, 19101, "Practice001")

    modify(df, 19122, "dateofinterview", "2017-04-07 21:35:00", None)