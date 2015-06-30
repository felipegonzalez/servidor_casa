library(dplyr)
library(tidyr)
library(lubridate)
library(ggplot2)
library(stringi)
library(jsonlite)

archivos <- list.files('./datos/estacion/', full.names = T)

lineas <- list()
linea.num <- 1
for(archivo in archivos){
  print(archivo)
  con <- file(archivo)
  open(con)
  linea <- readLines(con, n = 1)
  while (length(linea) > 0) {
    if(stri_detect_fixed(linea, 'Estacion') & stri_detect_fixed(linea, 'wind_speed')){
          lineas[[linea.num]] <- linea
          linea.num <- linea.num + 1
    }
    linea <- readLines(con, n = 1)
  } 
  close(con)
}
length(lineas)

lineas_sep <- lapply(1:length(lineas), function(i){
  lin <- lineas[[i]]
  #print(lin)
  temp_lin <- stri_split_fixed(lin, '|', n = 4)[[1]]
  hora <- temp_lin[2]
  datos_txt_1 <- stri_replace(temp_lin[4], '', fixed='Estacion:' )
  datos_txt_2 <- stri_replace_all(datos_txt_1, '\\"', regex="\\'")
  #print(datos_txt_2)
  out <- NULL
  if(nchar(datos_txt_2) > 3){
    out <- data.frame(fromJSON(datos_txt_2), stringsAsFactors = FALSE)
    out$datetime <- strftime(hora)
  }
  out
})


datos <- bind_rows(lineas_sep)
datos$datetime <- strptime(datos$datetime, format="%Y-%m-%d %H:%M:%S")
datos$date <- NULL
nrow(datos)
head(datos <- data.frame(datos))
datos$temperature <- as.numeric(datos$temperature)
datos$humidity <- as.numeric(datos$humidity)
datos$wind_speed <- as.numeric(datos$wind_speed)
datos$wind_direction <- as.numeric(datos$wind_direction)
datos$rain_mm_hour <- as.numeric(datos$rain_mm_hour)
datos$rain_mm_day <- as.numeric(datos$rain_mm_day)
saveRDS(datos, file = 'datos/datos_estacion.rds')
