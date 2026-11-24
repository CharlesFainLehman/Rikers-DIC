import time
import urllib.error

import pandas as pd
from datetime import date
from datetime import datetime
from datetime import timedelta

#note that the limit is 50,000 for the request is 50K. If for some reason
#there are more than 50K people on Rikers, this will break. But, uh, that's unlikely.
URL = 'https://data.cityofnewyork.us/resource/7479-ugqb.json?$limit=50000'
STORAGE_OPTIONS = {'X-App-Token':'p7zbW0RmUIiLtNo3XeA39pGY8'}

#NYC Open Data occasionally returns transient errors (e.g. 503 Service Unavailable),
#so retry with exponential backoff before giving up.
#Waits are 30s, 60s, 120s, 240s, 480s between attempts (~15 min total).
MAX_ATTEMPTS = 6
BASE_DELAY_SECONDS = 30
RETRYABLE_STATUS = {429, 500, 502, 503, 504}

def fetch_prisoners():
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return pd.read_json(URL, storage_options = STORAGE_OPTIONS)
        except urllib.error.HTTPError as e:
            if e.code not in RETRYABLE_STATUS or attempt == MAX_ATTEMPTS:
                raise
            err = "HTTP " + str(e.code) + " " + str(e.reason)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == MAX_ATTEMPTS:
                raise
            err = repr(e)
        delay = BASE_DELAY_SECONDS * 2 ** (attempt - 1)
        print("attempt " + str(attempt) + " failed (" + err + "); retrying in " + str(delay) + "s", flush=True)
        time.sleep(delay)

todays_prisoners = fetch_prisoners()

print("got file at " + str(datetime.now()))

#Basically, I run the github action at 4:25 AM UTC, so I get yesterday's file before it gets updated/don't risk github scheduling executing to get today's file tomorrow
#But to account for this, I label it as yesterday's file
yesterday = date.today() - timedelta(days = 1)
todays_prisoners.to_csv("./dat/via_github/DOC_Inmates_InCustody_Daily_" + yesterday.strftime("%Y%m%d") + ".csv", index=False)
