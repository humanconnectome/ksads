#!/usr/bin/env python3
import os
from datetime import datetime
from robobrowser import RoboBrowser
from ccf.config import LoadSettings

browser = RoboBrowser(history=True, timeout=6000, parser="lxml")

config = LoadSettings()["KSADS"]
download_dir = config["download_dir"]


def main():
    login()
    download_all()


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



if __name__ == "__main__":
    main()
