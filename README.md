This repository currently contains every "daily inmates in custody" file available from the NYC DOC between June 2, 2016 and June 1, 2022. The most recent version of the file, which changes daily, can be found here: https://data.cityofnewyork.us/Public-Safety/Daily-Inmates-In-Custody/7479-ugqb 

'daily files' contains the files. The subdirectory '06-02-2016 - 06-01-2022' contains the files obtained through FOIL. 

'bin' contains code. Cat_FOIL.R is an R script for concatenating them all into a single file. It should be executed form the top directory.

I am collecting each day's DIC file going forward, and hope to regularly add them to this repository. For now, these data are publicly available, and I will work to set up a more efficient pipeline for the archive going forward.
