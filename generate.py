# -*- coding: utf-8 -*-
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
import pandas as pd

import load_dataframes
from utils.utils import isna, escape_value
import utils.PandasHelper as h

ksads, current_redcap = load_dataframes.load()
# %% [markdown]
# # Keep the Status Quo

# %%
# print original shapes
# added = h.diff(ksads, current_redcap.id)
# deleted = h.diff(current_redcap, ksads.id)
# modified = h.conflict(current_redcap, ksads, intersect_on="id", sources=("redcap", "ksads.net"))
#
# print(ksads.shape, added.shape, deleted.shape, modified.shape)

# %%
import changes.accepted
df = ksads.set_index('id')
changes.accepted.execute(df)   # ACTION!
ksads = df.reset_index()

# %% [markdown]
# # Capture Changes

# %%
# print new shapes
added = h.diff(ksads, current_redcap.id)
deleted = h.diff(current_redcap, ksads.id)
modified = h.conflict(current_redcap, ksads, intersect_on="id", sources=("redcap", "ksads.net"))

print(ksads.shape, added.shape, deleted.shape, modified.shape)

# %%
# deleted is always empty, if not throw error
assert deleted.empty, "KSADS.net data has been deleted, take a look at `deleted` dataframe and figure out whether to delete those rows from redcap, Invalidate, mark a flag, or notify users etc."
deleted


file = open("changes/to_review.py", "w")
file.write("from changes.utils import block, modify\n\n\ndef execute(df):\n    pass\n")
# %%
def generate_blocking_code_for_added_rows(added):
    for _, row in added.iterrows():
        info = row.additionalinfo
        if pd.isna(info):
            info = "please_specify_reason"
        id_ = row.id
        d = row.iloc[1:6]    
        for k, v in d.items():
            print(f"    # {k}: {str(v)}", file=file)
        print(f'    block(df, {id_}, "{info}")\n', file=file)
generate_blocking_code_for_added_rows(added)


# %%
def generate_code_to_revert_modifications(df):
    for id_, group in modified.groupby('id'):
        redcap = group[group._merge == "redcap"].iloc[0]
        ksads = group[group._merge != "redcap"].iloc[0]

        cols = h.unequal_columns(group.iloc[:,:-1])
        print(f"\n    # {id_}", file=file)
        for col in cols:
            vr, vk = redcap[col], ksads[col]
            if isna(vr) and isna(vk):
                continue

            escaped_new = escape_value(ksads[col])
            escaped_permanent = escape_value(redcap[col])

            print(f'    modify(df, {id_}, "{col}", {escaped_new}, {escaped_permanent})', file=file)
generate_code_to_revert_modifications(df)

# %%

file.close()

# %%

# %%

# %%

# %% [markdown]
# ### Data Dictionary

# %%
#dd = RedcapTable.get_table_by_name('ksads').get_datadictionary()

#dd[dd.form_name == "common"]

