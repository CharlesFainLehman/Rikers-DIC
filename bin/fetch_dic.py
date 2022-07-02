import pandas as pd
from datetime import date
from datetime import datetime
from datetime import timedelta

#note that the limit is 50,000 for the request is 50K. If for some reason
#there are more than 50K people on Rikers, this will break. But, uh, that's unlikely.
todays_prisoners = pd.read_json('https://data.cityofnewyork.us/resource/7479-ugqb.json?$limit=50000', storage_options = {'X-App-Token':'p7zbW0RmUIiLtNo3XeA39pGY8'})

print("got file at " + str(datetime.now()))

#Basically, I run the github action at 4:25 AM UTC, so I get yesterday's file before it gets updated/don't risk github scheduling executing to get today's file tomorrow
#But to account for this, I label it as yesterday's file
yesterday = date.today() - timedelta(days = 1)
todays_prisoners.to_csv("./dat/via_github/DOC_Inmates_InCustody_Daily_" + yesterday.strftime("%Y%m%d") + ".csv", index=False)