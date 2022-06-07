library(tidyverse)

eight_to_date <- function(date){
  if(nchar(date) != 8) {break}
  year = substr(date, 1, 4)
  month = substr(date, 5, 6)
  day = substr(date, 7, 8)
  return(as.Date(paste(year, month, day, sep = "-")))
}

dic <- data.frame()

for(dir in list.dirs("./daily\ files/06-02-2016\ -\ 06-01-2022/")) {
  for(file in list.files(dir)){
    print(file)
    date <- eight_to_date(stringr::str_match(file, "\\d{8}")[1])
    read.csv(paste(dir, file, sep = "/")) %>%
      mutate(date = date) %>%
      bind_rows(dic) -> dic
  }
}

write.csv(dic, "DIC-06012016-06022022.csv", row.names = F)
