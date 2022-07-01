import os
import re
from datetime import date
from datetime import datetime

for f in os.listdir():
    if re.match("dic-", f):
        file_date_str = re.findall("(\w+) (\d\d), (\d\d\d\d)", f)
        file_date_date = date(int(file_date_str[0][2]), datetime.strptime(file_date_str[0][0], '%B').month, int(file_date_str[0][1]))
        os.rename(f,"DOC_Inmates_InCustody_Daily_" + file_date_date.strftime("%Y%m%d") + ".csv")