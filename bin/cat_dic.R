library(vroom)
library(tidyverse)
library(stringr)

if(file.exists("dat/combined.csv")) {
  file.remove("dat/combined.csv")
}

n.files <- length(list.files("dat/", recursive = T, pattern = '\\.csv'))
i = 0

for (file in list.files("dat/", recursive = T, pattern = '\\.csv')) {
  print(scales::percent(i/n.files))
  i <- i + 1
  
  date <- as.Date((str_match(file, "\\d{8}\\.csv")[[1]]), format = '%Y%m%d')
  vroom(paste('dat/', file, sep = ""), delim = ',', show_col_types = F, progress = T) %>%
    mutate(DATE = date) %>%
    write.table("dat/combined.csv", append = T, sep = ',', row.names = F, col.names = F)
}