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



### datos de pirs
#dat_todos <- collect(dat_1, n=-1)
pirs <- filter(dat_todos, tipo == 'pir')
pirs$tiempo <- strptime(pirs$tiempo_reg, "%Y-%m-%d %H:%M:%S", tz="America/Mexico_City")    

ggplot(pirs, aes(x=tiempo, y=valor, colour=lugar, shape=num_sensor, 
                 group=interaction(lugar, num_sensor))) + 
    geom_point() + facet_wrap(~lugar) +
    geom_smooth(se=FALSE, span=10, method='loess', degree=1)

##############
load('base_ejemplo_casa.Rdata')
dat_todos$tiempo <- strptime(dat_todos$tiempo_reg, "%Y-%m-%d %H:%M:%S", tz="America/Mexico_City")
dat_todos$mes <- month(dat_todos$tiempo)
dat_todos$day <- day(dat_todos$tiempo)
dat_todos$hour <- hour(dat_todos$tiempo)
tiempo <- dat_todos$tiempo
dat_todos$tiempo <- NULL
dat_todos %>%
    group_by(mes, day, hour) %>%
    summarise(n=n()) %>%
    data.frame()
dat_todos$tiempo <- tiempo
dat_5 <- filter(dat_todos, mes==1)

ggplot(filter(dat_5, tipo=='temperature')),
    aes()