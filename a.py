import os
import re

import numpy as np
import pandas as pd
from IPython.core.display import display, HTML

import utils.PandasHelper as h
from ksads_notebook import olddate, newdate, table, studyids, studydata, downloads_dir


def special_quotes(x):
    quotes = re.compile("[“”]")
    return x.apply(
        lambda x: x.astype(str).str.replace(quotes, '"').str.replace("’", "'")
        if x.dtype == "O"
        else x
    )


class KsadForm:
    def __init__(self, form):
        self.form = form
        self.form_complete = form + "_complete"
        self.old = read_csv(olddate, form)
        self.new = read_csv(newdate, form)
        redcap_df = table.get_frame(forms=["common", form])
        redcap_df = redcap_df[redcap_df[self.form_complete] == 1]
        self.redcap_df = redcap_df
        self.update()

    def update(self):
        make_similar(self.old, self.new)
        self.deleted = h.diff(self.old, self.new.id)
        self.modified = h.intersection(self.old, self.new, "id").sort_values("id")
        added = h.diff(self.new, self.old.id)
        added[self.form_complete] = 1
        added["common_complete"] = 1
        make_similar(added, self.redcap_df)
        added = h.diff(added, self.redcap_df)
        self.added = added

        if added is not None and not added.empty:
            self.merged = self.redcap_df.append(added, sort=False)
        else:
            self.merged = self.redcap_df

    def show_deleted_rows(self):
        form, added, deleted, modified = self.form, self.added, self.deleted, self.modified
        if not deleted.empty:
            h.showbox(
                """There are %s rows in the old data that has been removed in the new data.
                            If this is expected, you can ignore this message.
                            To further inspect rows type <code>data["deleted"]</code>"""
                % len(deleted),
                form + ": Deleted",
                "danger",
                )
            h.showdataframe(deleted)


    def show_modified_rows(self):
        form, added, deleted, modified = self.form, self.added, self.deleted, self.modified
        if not modified.empty:
            h.showbox(
                """There are %s rows in the old data that has been modified in the new data.
                            If this is expected, you can ignore this message.
                            To further inspect rows type <code>data["modified"]</code>"""
                % len(modified),
                form + ": Modified",
                "danger",
                )
            h.showdataframe(modified)

    def warn_duplicates(self):
        form, added, deleted, modified = self.form, self.added, self.deleted, self.modified
        duplicates = df[df.duplicated(['patientid', 'patienttype'], keep=False)]
        duplicates['reason'] = 'Duplicate IDs'
        if duplicates.empty:
            h.showbox(
                """All patientid + patienttype combos are unique.""",
                form + ": No Duplicates",
                "success",
                )
        else:
            h.showbox(
                """There are %s rows that contain the same patientid + patienttype."""
                % len(duplicates),
                form + ": Duplicates",
                "danger",
                )
            h.showdataframe(duplicates)
            # raise Exception()

    def show_additional_info(self):
        form, added, deleted, modified = self.form, self.added, self.deleted, self.modified
        show = self.added.dropna(subset=["additionalinfo"]).iloc[:, :6]
        if not show.empty:
            display(
                HTML(
                    "<H3>Additional Info</H3><SMALL> Please read the additional info columns for possible clarifications/corrections</SMALL>"
                )
            )
            display(ipysheet.sheet(ipysheet.from_dataframe(show)))

    def show_modified(self):
        form, added, deleted, modified = self.form, self.added, self.deleted, self.modified
        def update(btn):
            self.added = (
                dups.loc[[dd.value for dd in selections]]
                .iloc[:, :-1]
                .append(self.added, sort=False)
                .drop_duplicates(["patientid", "patienttype"])
            )

        btn = wg.Button(description="Submit changes")
        btn.on_click(update)

        dups = h.intersection(
            self.redcap_df,
            self.added,
            ["patientid", "patienttype"],
            sources=("current", "new"),
        ).reset_index(drop=True)
        selections = []
        output = []
        for id, group in dups.groupby("id"):
            cols = ["id", "patientid"] + h.unequal_columns(group)
            show = group[cols].set_index("_merge")
            sheet = ipysheet.sheet(ipysheet.from_dataframe(show))
            options = [(k, v) for v, k in group._merge.items()]

            dd = wg.Dropdown(
                options=options,
                value=options[0][1],
                description="Keep version:",
                disabled=False,
            )
            selections.append(dd)
            output.append(sheet)
            output.append(dd)

        if output:
            display(
                HTML(
                    "<H3>Should New Data Overwrite Old Data</H3><SMALL>Please select which version to keep.</SMALL>"
                )
            )
            for x in output:
                display(x)
            display(btn)

    def warn_not_in_redcap(not_in_redcap, form):
        not_in_redcap = h.difference(df, studyids.subject).copy()
        not_in_redcap['reason'] = 'PatientID not in Redcap'
        not_in_redcap.rename(columns={'sitename': 'site'}, inplace=True)

        if not_in_redcap.empty:
            h.showbox(
                """All patientid's are in Redcap.""",
                form + ": No Subject Missing from Redcap",
                "success",
                )
        else:
            h.showbox(
                """There are %s rows with patientid missing from Redcap."""
                % len(not_in_redcap),
                form + ": Subjects Missing from Redcap",
                "danger",
                )
            h.showdataframe(not_in_redcap)

    def show_not_in_redcap(self):
        form, added, deleted, modified = self.form, self.added, self.deleted, self.modified
        df = self.merged.copy()
        df["subject"] = df["patientid"].str.split("_", 1, expand=True)[0].str.strip()
        not_in_redcap = h.diff(df, studyids.subject).iloc[:, :-1]
        h.asInt(not_in_redcap, "id", "common_complete", self.form_complete)
        not_in_redcap.insert(0, "delete", False)
        not_in_redcap.insert(1, "link", "view")

        sheet = ipysheet.sheet(ipysheet.from_dataframe(not_in_redcap))

        spaced = wg.Layout(margin="30px 0 20px 0")

        save_btn = wg.Button(description="Update", icon="save")
        reset_btn = wg.Button(description="Reset", icon="trash")
        btns = wg.HBox([save_btn, reset_btn], layout=spaced)

        def on_reset(btn):
            sheet.cells = ipysheet.from_dataframe(not_in_redcap).cells

        #     sheet = ipysheet.sheet(ipysheet.from_dataframe(not_in_redcap))

        reset_btn.on_click(on_reset)

        def on_update(btn):
            df = ipysheet.to_dataframe(sheet)
            df = df.replace("nan", np.nan)

            # delta  of changes
            z = h.diff(df, not_in_redcap)

            updates = z[~z.delete].iloc[:, 1:]
            if not updates.empty:
                r = table.send_frame(updates)
                print("Updates: ", r.status_code, r.content)

            delete = z[z.delete].id.tolist()
            if delete:
                r = table.delete_records(delete)
                print("Delete Records: ", r.status_code, r.content)

        save_btn.on_click(on_update)

        fancy_widget = wg.VBox([sheet, btns])

        def convert_to_links():
            values = [
                wg.HTML(
                    '<a target="_blank" href="https://redcap.wustl.edu/redcap/redcap_v8.11.0/DataEntry/record_home.php?pid=3355&arm=1&id=%s">view</a>'
                    % x
                )
                for x in sheet.cells[2].value
            ]
            ipysheet.column(1, values)

        convert_to_links()
        if not not_in_redcap.empty:
            display(
                HTML(
                    "<H3>Subject IDs not in Redcap</H3><SMALL>Please either change patientid to match an ID in redcap or delete the row.</SMALL>"
                )
            )
            display(fancy_widget)

    def show_missing_subjects(self):
        form, added, deleted, modified = self.form, self.added, self.deleted, self.modified
        df = self.merged.copy()
        df["subject"] = df["patientid"].str.split("_", 1, expand=True)[0].str.strip()
        missing = h.diff(studydata, df.subject)

        # missing = h.difference(studydata, df.subject).copy()
        missing = missing[missing.flagged.isnull()]
        missing = missing[missing.interview_date < "2019-05-01"]
        missing = missing[missing.study != "hcpa"]
        missing["reason"] = "Missing in Box"
        self.warn_missing(missing, self.form)
        display(missing)
        return missing
        # data['missing'] = missing
        # ksads.warn_missing(missing, form)

    def warn_missing(self, missing, form):
        if missing.empty:
            h.showbox(
                """All patientid's are in New Data.""",
                form + ": No Missing Redcap Subjects",
                "success",
                )
        else:
            h.showbox(
                """There are %s Redcap subjects missing from the current data."""
                % len(missing),
                form + ": Redcap Subjects Missing",
                "danger",
                )
            h.showdataframe(missing)

    @staticmethod
    def warn_good_import(added, deleted, form, modified):
        if deleted.empty and modified.empty:
            h.showbox(
                """There are %s rows of new data and no unexpected changes to old data.
                            Please proceed with <code>data["raw"]</code>."""
                % len(added),
                form + ": Importing Data",
                "success",
                )
            h.showdataframe(added)

def read_csv(date, form):
    df = pd.read_csv(os.path.join(downloads_dir, date, form + ".csv"), low_memory=False)
    return special_quotes(df)


def make_similar(df1, df2):
    for name, column in df1.items():
        if name in df2.columns:
            dtype = column.dtype if column.notna().any() else df2[name].dtype
            df2[name] = df2[name].astype(dtype)
            df1[name] = df1[name].astype(dtype)