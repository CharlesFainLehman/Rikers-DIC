"""Concatenate every daily DIC file under dat/ into one CSV for analysis.

Writes incrementally (one daily file at a time) so memory use stays flat
even with thousands of input files.

Output: dat/processed/DOC_Inmates_InCustody_Daily_full.csv
"""

import os
import re
from datetime import datetime

import pandas as pd

OUT_DIR = os.path.join("dat", "processed")
OUT_PATH = os.path.join(OUT_DIR, "DOC_Inmates_InCustody_Daily_full.csv")

# Column names vary across files in case and order, and some files lack
# discharged_dt entirely; normalize to this schema.
COLUMNS = [
    "inmateid", "admitted_dt", "discharged_dt", "custody_level", "bradh",
    "race", "gender", "age", "inmate_status_code", "sealed", "srg_flg",
    "top_charge", "infraction", "date",
]

FILENAME_RE = re.compile(r"DOC_Inmates_InCustody_Daily_(\d{8})\.csv$")


def daily_files():
    for root, dirs, files in os.walk("dat/"):
        # Don't re-ingest our own output.
        dirs[:] = [d for d in dirs if d != "processed"]
        for name in sorted(files):
            match = FILENAME_RE.search(name)
            if match is not None:
                yield os.path.join(root, name), match.group(1)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp_path = OUT_PATH + ".tmp"

    n_files = 0
    n_rows = 0
    with open(tmp_path, "w", newline="") as out:
        for path, date_str in daily_files():
            file_date = datetime.strptime(date_str, "%Y%m%d")
            day = pd.read_csv(path, low_memory=False)
            day.columns = day.columns.str.lower()
            day["date"] = file_date
            for col in COLUMNS:
                if col not in day.columns:
                    day[col] = pd.NA
            day[COLUMNS].to_csv(out, index=False, header=(n_files == 0))
            n_files += 1
            n_rows += len(day)
            if n_files % 250 == 0:
                print(f"{n_files} files, {n_rows} rows so far...")

    if n_files == 0:
        os.remove(tmp_path)
        raise SystemExit("no daily files found under dat/")

    os.replace(tmp_path, OUT_PATH)
    print(f"wrote {n_rows} rows from {n_files} files to {OUT_PATH}")


if __name__ == "__main__":
    main()
