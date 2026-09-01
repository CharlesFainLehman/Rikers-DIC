library(vroom)
library(tidyverse)
library(stringr)

# Concatenate every daily DIC file under dat/ into dat/combined.csv.

out.path <- "dat/combined.csv"

if (file.exists(out.path)) {
  file.remove(out.path)
}

# Canonical column order; some files lack discharged_dt, and column order
# varies across files, so columns are aligned by name below.
col.order <- c("inmateid", "admitted_dt", "discharged_dt", "custody_level",
               "bradh", "race", "gender", "age", "inmate_status_code",
               "sealed", "srg_flg", "top_charge", "infraction", "date")

data.frame(inmateid = double(), admitted_dt = character(), discharged_dt = character(),
           custody_level = character(), bradh = character(), race = character(),
           gender = character(), age = double(), inmate_status_code = character(),
           sealed = character(), srg_flg = character(), top_charge = character(),
           infraction = character(), date = character()) %>%
  write.table(out.path, sep = ',', row.names = F)

# Only match the daily files themselves, so combined.csv and anything in
# dat/processed/ can't get swept back in.
dic.files <- list.files("dat/", recursive = T,
                        pattern = 'DOC_Inmates_InCustody_Daily_\\d{8}\\.csv$')

n.files <- length(dic.files)
i <- 0

for (file in dic.files) {
  i <- i + 1
  print(paste0(file, " (", i, "/", n.files, ")"))

  date <- as.Date(str_match(file, "(\\d{8})\\.csv$")[[2]], format = '%Y%m%d')
  dic <- vroom(paste0('dat/', file), delim = ',', show_col_types = F, progress = F)
  names(dic) <- tolower(names(dic))
  dic$date <- date

  # Some files do not have a discharged_dt column; add it so every file
  # matches the canonical schema, then align columns by name.
  if (!('discharged_dt' %in% names(dic))) {
    dic$discharged_dt <- NA
  }
  dic <- select(dic, all_of(col.order))

  write.table(dic, out.path, append = T, sep = ',', row.names = F, col.names = F)
}
