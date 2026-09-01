"""Fetch the NYC DOC "Daily Inmates In Custody" snapshot and save it as a
dated CSV in dat/via_github/.

The workflow runs this shortly after midnight ET, so the snapshot on the
portal still reflects "yesterday" and the file is labeled with yesterday's
date (America/New_York). A later retry run is safe: if the target file
already exists the script exits without touching it, and if the portal has
already rolled over to a newer snapshot the metadata check below catches
the mismatch and the script aborts rather than saving a mislabeled file.
"""

import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

DATASET_ID = "7479-ugqb"
DATA_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json?$limit=100000"
METADATA_URL = f"https://data.cityofnewyork.us/api/views/{DATASET_ID}.json"
# X-App-Token is a rate-limiting identifier, not a secret; override via env if needed.
APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN", "p7zbW0RmUIiLtNo3XeA39pGY8")
ROW_LIMIT = 100000
MAX_ATTEMPTS = 5
NYC_TZ = ZoneInfo("America/New_York")

# Canonical column order. The JSON API returns keys in unstable order and
# drops columns that are null for every row, so we normalize here.
EXPECTED_COLUMNS = [
    "inmateid",
    "admitted_dt",
    "custody_level",
    "bradh",
    "race",
    "gender",
    "age",
    "inmate_status_code",
    "sealed",
    "srg_flg",
    "top_charge",
    "infraction",
]

# Any plausible daily census is well above this; fewer rows means a bad response.
MIN_EXPECTED_ROWS = 1000


def http_get(url, headers=None, timeout=120):
    """GET a URL with retries and exponential backoff. Returns bytes."""
    last_err = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as err:
            last_err = err
            wait = 2 ** attempt  # 2, 4, 8, 16, 32 seconds
            print(
                f"attempt {attempt}/{MAX_ATTEMPTS} failed ({err}); "
                f"retrying in {wait}s",
                file=sys.stderr,
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(wait)
    raise RuntimeError(f"all {MAX_ATTEMPTS} attempts failed: {last_err}")


def snapshot_date():
    """Date label for today's snapshot: yesterday in UTC.

    The primary run fires at 04:25 UTC, which is 12:25 AM ET in summer and
    11:25 PM ET in winter. In both cases the snapshot on the portal was
    published the previous UTC day, so "UTC today minus one" is the right
    label year-round (this matches the original script's behavior). The
    vintage check below guards the retry runs against the portal rolling
    over to a newer snapshot.
    """
    return datetime.now(timezone.utc).date() - timedelta(days=1)


def check_snapshot_vintage(label_date):
    """Cross-check the dataset's last-update time against the date we plan
    to label the file with. Non-fatal if the metadata endpoint is down."""
    try:
        meta = json.loads(http_get(METADATA_URL, headers={"X-App-Token": APP_TOKEN}))
        updated_at = datetime.fromtimestamp(meta["rowsUpdatedAt"], tz=timezone.utc)
        updated_date = updated_at.astimezone(NYC_TZ).date()
        print(f"dataset rowsUpdatedAt: {updated_at.isoformat()} (ET date {updated_date})")
        if updated_date > label_date:
            # Portal already holds a newer snapshot than the date we would
            # write. Saving it as label_date would mislabel the data.
            print(
                f"ERROR: snapshot was updated {updated_date} but we would label it "
                f"{label_date}; refusing to save a mislabeled file.",
                file=sys.stderr,
            )
            sys.exit(1)
    except SystemExit:
        raise
    except Exception as err:  # metadata check is best-effort
        print(f"warning: could not verify snapshot vintage: {err}", file=sys.stderr)


def main():
    label_date = snapshot_date()
    out_path = os.path.join(
        "dat", "via_github",
        f"DOC_Inmates_InCustody_Daily_{label_date.strftime('%Y%m%d')}.csv",
    )

    if os.path.exists(out_path):
        print(f"{out_path} already exists; nothing to do.")
        return

    check_snapshot_vintage(label_date)

    raw = http_get(DATA_URL, headers={"X-App-Token": APP_TOKEN})
    print(f"got file at {datetime.now()}")

    # Parse with pandas the same way the original script did, so dtypes
    # (and therefore the CSV text) stay consistent with existing files.
    dic = pd.read_json(io.StringIO(raw.decode("utf-8")))

    if len(dic) < MIN_EXPECTED_ROWS:
        print(
            f"ERROR: only {len(dic)} rows returned; refusing to save what looks "
            "like a bad or empty response.",
            file=sys.stderr,
        )
        sys.exit(1)
    if len(dic) >= ROW_LIMIT:
        print(
            f"ERROR: hit the {ROW_LIMIT}-row limit; the snapshot may be truncated.",
            file=sys.stderr,
        )
        sys.exit(1)

    missing = [c for c in EXPECTED_COLUMNS if c not in dic.columns]
    if len(missing) > 2:
        print(f"ERROR: response is missing expected columns: {missing}", file=sys.stderr)
        sys.exit(1)
    for col in missing:
        # A column that is null for every row is dropped by the API; add it
        # back empty so every file has the same schema.
        print(f"warning: column {col!r} absent from response; filling with NA")
        dic[col] = pd.NA

    extra = [c for c in dic.columns if c not in EXPECTED_COLUMNS]
    if extra:
        print(f"warning: response has new columns, keeping them at the end: {extra}")
    dic = dic[EXPECTED_COLUMNS + extra]

    tmp_path = out_path + ".tmp"
    dic.to_csv(tmp_path, index=False)
    os.replace(tmp_path, out_path)
    print(f"wrote {len(dic)} rows to {out_path}")


if __name__ == "__main__":
    main()
