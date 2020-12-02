# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.5.2
#   kernelspec:
#     display_name: ksads
#     language: python
#     name: ksads
# ---

# %%
import os
from collections import defaultdict
from datetime import datetime
import pandas as pd
import re


# %%
def generate_snapshot_from_raw_excel_files(d = "2020-12-02"):
    prefix = f"./cache/{d}"

    dataframes = defaultdict(list)
    for filename in os.listdir(prefix):
        sitename, form = re.search("([^-]+)-(.+?)\.xlsx", filename).groups()
        filename = f"{prefix}/{filename}"
        df = pd.read_excel(filename, parse_dates=["DateofInterview"])
        dataframes[form].append(df)

    new_dfs = {}
    for form, dfs in dataframes.items():
        df = pd.concat(dfs, sort=False).sort_values(["DateofInterview", "ID"])

        df.columns = [
            "ksads" + label if isnumeric else label.lower()
            for label, isnumeric in zip(df.columns, df.columns.str.isnumeric())
        ]
        df[f"{form}_complete"] = 1
        new_dfs[form] = df

    combined = new_dfs['intro'].merge(new_dfs['screener'], how="outer").merge(new_dfs['supplement'], how="outer")
    print(d,combined.shape)
    combined.to_csv(f'./cache/snapshot.{d}.csv', index=False)



# %%
def generate_snapshot_from_old_combined_csv(d):
    prefix = f"./cache/{d}"

    intro = pd.read_csv(f"{prefix}/intro.csv", low_memory=False)
    screener = pd.read_csv(f"{prefix}/screener.csv", low_memory=False)
    supplement = pd.read_csv(f"{prefix}/supplement.csv", low_memory=False)

    intro["intro_complete"] = 1
    screener["screener_complete"] = 1
    supplement["supplement_complete"] = 1

#     intro = intro.set_index('id')
#     screener = screener.set_index('id')
#     supplement = supplement.set_index('id')
    combined = intro.merge(screener, how="outer").merge(supplement, how="outer")
    print(d,combined.shape)

    combined.to_csv(f'./cache/snapshot.{d}.csv', index=False)


# %%
if __name__ == "__main__":
    for d in sorted(os.listdir('./cache/')):
        if os.path.isdir(prefix):
            generate_snapshot_from_old_combined_csv(d)

