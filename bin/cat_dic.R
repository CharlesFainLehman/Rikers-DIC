library(vroom)
library(tidyverse)
library(stringr)

if(file.exists("dat/combined.csv")) {
  file.remove("dat/combined.csv")
}

data.frame(inmateid = double(), admitted_dt = character(), discharged_dt = logical(),
           custody_level = character(), bradh = character(), race = character(),
           gender = character(), age = double(), inmate_status_code = character(),
           sealed = character(), srg_flg = character(), top_charge = character(),
           infraction = character(), date = character()) %>%
  write.table("dat/combined.csv", sep = ',', row.names = F)


n.files <- length(list.files("dat/", recursive = T, pattern = '\\.csv'))
i = 0

for (file in list.files("dat/", recursive = T, pattern = '\\.csv')) {
  print(file)
  #print(scales::percent(i/n.files))
  i <- i + 1
  
  date <- as.Date((str_match(file, "\\d{8}\\.csv")[[1]]), format = '%Y%m%d')
  dic <- vroom(paste('dat/', file, sep = ""), delim = ',', show_col_types = F, progress = T) %>%
    mutate(DATE = date)
  names(dic) <- tolower(names(dic))
  
  #this psycho little kludge deals with the fact that some
  #of the later files do not have a discharged_dt column
  dic.names <- names(dic)
  
  if(!('discharged_dt' %in% dic.names)) {
    dic$discharged_dt <- NA
    dic <- select(dic, dic.names[1:2], 'discharged_dt', dic.names[3:length(dic.names)])
  }
  
  write.table(dic, "dat/combined.csv", append = T, sep = ',', row.names = F, col.names = F)
}