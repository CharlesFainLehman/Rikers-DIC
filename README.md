As of the most recent update of this Readme, this repository contains every "daily inmates in custody" file available from the NYC DOC between June 2, 2016 and the day before whatever the current day is. The most recent version of the file, which changes daily, can be found here: https://data.cityofnewyork.us/Public-Safety/Daily-Inmates-In-Custody/7479-ugqb 

dat/ contains the files. They come form three sources. Files I obtained through FOIL — covering, roughly, 6/2/16 through 6/1/2022 — are in the foil/ folder. Files I downloaded manually for about a month are in manual/. Files obtained through a Python script now executed through Github actions are in via_github/. Note that every file is essentially the same. They don't contain a date column, so the date has to be pulled out of the name of the file.

bin/ contains scripts for the project. As of the most recent update, all that's in there is the Python script that Github actions executes.

This repository should update with the latest file every morning at around 12:30 AM ET.
