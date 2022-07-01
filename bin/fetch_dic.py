import pandas as pd
from datetime import date

#note that the limit is 50,000 for the request is 50K. If for some reason
#there are more than 50K people on Rikers, this will break. But, uh, that's unlikely.
todays_prisoners = pd.read_json('https://data.cityofnewyork.us/resource/7479-ugqb.json?$limit=50000', storage_options = {'X-App-Token':'p7zbW0RmUIiLtNo3XeA39pGY8'})

#DOC_Inmates_InCustody_Daily_20160602
todays_prisoners.to_csv("dat/via_github/DOC_Inmates_InCustody_Daily_" + date.today().strftime("%Y%m%d"))