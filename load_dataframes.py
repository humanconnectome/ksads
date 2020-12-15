import os

import pandas as pd
from ccf.config import LoadSettings
from ccf.redcap import CachedRedcap

from utils.utils import strip_special_chars, to_numeric, convert_nan, synchronize_dtypes


def load():
    config = LoadSettings()
    downloads_dir = config["KSADS"]["download_dir"]
    snapshots = [os.path.join(downloads_dir, x) for x in sorted(os.listdir(downloads_dir)) if x.startswith("snapshot")]

    latest_snapshot = snapshots[-1]
    print("Latest snapshot is ", latest_snapshot)

    # %%
    ksads = pd.read_csv(latest_snapshot, low_memory=False)
    ksads = strip_special_chars(ksads)
    ksads.dateofinterview = pd.to_datetime(ksads.dateofinterview)
    complete_columns = ksads.columns[ksads.columns.str.endswith("_complete")]
    ksads["common_complete"] = 1
    ksads[complete_columns] = ksads[complete_columns].mask(ksads[complete_columns].isna(), 0).astype(int)

    # %%
    redcap = CachedRedcap()
    current_redcap = redcap("ksads")
    current_redcap.dateofinterview = pd.to_datetime(current_redcap.dateofinterview)

    # Make compatible

    # %%
    ksads = ksads.apply(to_numeric)
    current_redcap = current_redcap.apply(to_numeric)
    ksads = convert_nan(ksads)
    current_redcap = convert_nan(current_redcap)
    synchronize_dtypes(current_redcap, ksads)

    # %%
    # add redcap only columns, eg "k_unusable"
    unique_to_redcap = list(current_redcap.columns.difference(ksads.columns))
    ksads = ksads.merge(current_redcap[unique_to_redcap + ["id"]], how="left", on="id")

    return ksads, current_redcap