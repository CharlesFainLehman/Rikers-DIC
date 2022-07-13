import pandas as pd
from datetime import datetime
import os
import re

final_dic = pd.DataFrame()

for root, dirs, files in os.walk("dat/", topdown=False):
   for name in files:
       date_str = re.search('\d{8}', name)
       if date_str == None: #if there's a match
           next
       else:
           date = datetime.strptime(date_str.group(0), "%Y%m%d") #the scoping here alarms me
       print(date)
       date_dic = pd.read_csv(os.path.join(root, name))
       date_dic['date'] = date
       final_dic = pd.concat([final_dic, date_dic])

final_dic.to_csv('dat/processed/DOC_Inmates_InCustody_Daily_full.csv', index = False)