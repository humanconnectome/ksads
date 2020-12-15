#!/usr/bin/env python3
import os
import re
from collections import defaultdict
from datetime import datetime
from robobrowser import RoboBrowser
from ccf.config import LoadSettings
import pandas as pd

browser = RoboBrowser(history=True, timeout=6000, parser="lxml")

config = LoadSettings()["KSADS"]
download_dir = config["download_dir"]


def main():
    login()
    download_all()
    generate_snapshot_from_raw_excel_files()


def login():
    browser.open("https://ksads.net/Login.aspx")
    form = browser.get_form("form1")
    form["txtUsername"].value = config["user"]
    form["txtPassword"].value = config["password"]
    browser.submit_form(form)

    if browser.response.url == "https://ksads.net/Login.aspx":
        raise Exception("Incorrect credentials provided")
        return False
    else:
        print("Logged in.")
        return True


def download(siteid, studytype, name):
    # submit the report "type"
    print('Requesting "%s" from "%s"' % (studytype, name))
    browser.open("https://ksads.net/Report/OverallReport.aspx")
    form = browser.get_form("form1")
    form["ddlGroupName"].value = str(siteid)
    form["chkUserType"].value = studytype
    browser.submit_form(form, form["btnexecute"])

    # request the results
    form = browser.get_form("form1")
    form["ddlGroupName"].value = str(siteid)
    form["chkUserType"].value = studytype
    browser.submit_form(form, form["btnexportexcel"])

    # save results to file
    timestamp = datetime.today().strftime("%Y-%m-%d")
    filename = f"{download_dir}/{timestamp}/{name}-{studytype}.xlsx"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if browser.response.ok:
        content = browser.response.content
        if content:
            print("Saving file %s" % filename)
            with open(filename, "wb+") as fd:
                fd.write(content)


def download_all():
    """
    Download the KSADS excel files. Returns the list of files downloaded.
    """

    studytypes = config["forms"]

    # go through ever iteration of study site/type
    for studytype in studytypes:
        for name, siteid in config["siteids"].items():
            download(siteid, studytype, name)

    print("Download complete.")


def generate_snapshot_from_raw_excel_files(timestamp=None):
    if timestamp is None:
        timestamp = datetime.today().strftime("%Y-%m-%d")
    prefix = f"{download_dir}/{timestamp}/"

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

    combined = (
        new_dfs["intro"]
        .merge(new_dfs["screener"], how="outer")
        .merge(new_dfs["supplement"], how="outer")
    )
    print(timestamp, combined.shape)
    combined.to_csv(f"{download_dir}/snapshot.{timestamp}.csv", index=False)


if __name__ == "__main__":
    main()
