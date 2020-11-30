#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ccf.config import LoadSettings
from ccf.redcap import CachedRedcap
from a import special_quotes, KsadForm, read_csv

# %%
redcap = CachedRedcap()

table = redcap("ksads")
studyids = redcap.get_behavioral_ids()
studydata = studyids[studyids.study != "parent"]

config = LoadSettings()
downloads_dir = config["KSADS"]["download_dir"]
dates = sorted(os.listdir(downloads_dir))

# %%
olddate = dates[0]
newdate = dates[-1]

# %%
df = read_csv(dates[-1], "intro")
df = special_quotes(df)

# %%
df


# %%
intro = KsadForm("intro")
intro.show_additional_info()
intro.show_deleted_rows()
intro.show_modified_rows()
intro.show_modified()
intro.show_not_in_redcap()
intro.show_missing_subjects()

# %%
screener = KsadForm("screener")
screener.show_additional_info()
screener.show_deleted_rows()
screener.show_modified_rows()
screener.show_modified()
screener.show_not_in_redcap()
screener.show_missing_subjects()

# %%
supplement = KsadForm("supplement")
supplement.show_additional_info()
supplement.show_deleted_rows()
supplement.show_modified_rows()
supplement.show_modified()
supplement.show_not_in_redcap()
supplement.show_missing_subjects()

# %%
from ccf.redcap import CachedRedcap, RedcapTable

redcap = CachedRedcap()
table = redcap("ksads")

# %%
ksads = RedcapTable.get_table_by_name("ksads")

# %%
ksads.send_frame(intro.added)

# %%
r = ksads.send_frame(screener.added)
r.json()

# %%
r = ksads.send_frame(supplement.added)
r.json()

# %%
intro.added

