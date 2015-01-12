library(dplyr)
library(tidyr)
library(ggplot2)
library(lubridate)
my_db <- src_mysql(host='192.168.100.50', user='root', password='',
                   dbname='casa')
mediciones <- tbl(my_db, "mediciones")

dat_1 <- tbl(my_db, sql("select * from mediciones where ts > DATE_SUB( NOW(), INTERVAL 6000 MINUTE )")) 
#dat_1 <- tbl(my_db, sql("select * from mediciones") )
dat_2 <- filter(dat_1, tipo=='temperature',lugar=='tv') %>% data.frame
dat_3 <- filter(dat_1, tipo=='gaslpg') %>% data.frame
dat_2$tiempo <- strptime(dat_2$tiempo_reg, "%Y-%m-%d %H:%M:%S", tz="America/Mexico_City")    
dat_3$tiempo <- strptime(dat_3$tiempo_reg, "%Y-%m-%d %H:%M:%S", tz="America/Mexico_City")    
ggplot(dat_2, aes(x=tiempo, y=valor, colour=num_sensor)) + geom_line() + geom_point()
ggplot(dat_3, aes(x=tiempo, y=valor, colour=lugar, group=lugar)) + geom_line()
