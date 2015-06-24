import dweepy
import requests
import time
import datetime
import json
import phant
import logging
import logging.handlers
import math
import sqlite3 as lite
import re

con = lite.connect('/Volumes/mmshared/bdatos/ultimas.db')
## logging
format_logging = logging.Formatter(fmt='%(levelname)s|%(asctime)s|%(name)s| %(message)s ', datefmt="%Y-%m-%d %H:%M:%S")
h = logging.handlers.TimedRotatingFileHandler('/Volumes/mmshared/bdatos/log/monitor/estacion_meteo.log', encoding='utf8',
        interval=1, when='midnight', backupCount=4000)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
h.setFormatter(format_logging)
h.setLevel(logging.DEBUG)
root_logger.addHandler(h)

inicial_lluvia_hora = 0
hour_anterior = datetime.datetime.now().hour

url_wunder = 'http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?'
id_wunder = 'IDISTRIT49' 
#pass_wunder= 'A34-Qg6-272-6Jq'
pass_wunder = 'valqui1'
#http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?ID=KCASANFR5&PASSWORD=XXXXXX&dateutc=2000-01-01+10%3A32%3A35&winddir=230&windspeedmph=12&windgustmph=12&tempf=70&rainin=0&baromin=29.1&dewptf=68.2&humidity=90&weather=&clouds=&softwaretype=vws%20versionxx&action=updateraw
url_1 = url_wunder + 'ID='+id_wunder+'&PASSWORD='+pass_wunder
#p = phant.Phant("XGvXXOnn1aFKYpJGvV6r", 'temperature','humidity',
#   'wind_direction','wind_speed','rain_mm_day',private_key = "1J0ggV88qKtMbqDnN64x")
while(True):

    try:
        r = requests.get('http://estacionyun.local/arduino/weather/0', timeout=20)
        print('Dweeting')
        print(r.text.strip("\r\n"))
        logging.info('Estacion:'+r.text.strip("\r\n"))
        d = json.loads(r.text.strip("\r\n").replace("'", "\""))
        print d
        try:
            dweepy.dweet_for('rich-honey', d)
        except:
            print("error dweepy")
            logging.error('Error dweepy')

        #weather underground
        hour_actual = datetime.datetime.now().hour
        if(hour_actual != hour_anterior):
            inicial_lluvia_hora = float(d['rain_mm_day'])
            hour_anterior = hour_actual
        acumulado_lluvia_hora = float(d['rain_mm_day']) - inicial_lluvia_hora   
        print 'Acumulado hora lluvia: %s'  % acumulado_lluvia_hora
        print 'Hora ant %s, actual %s' % (hour_anterior, hour_actual)
        try:
            rh = float(d['humidity'])
            tc = float(d['temperature'])
            #h = (math.log10(rh) -2.0)/0.4343 + (17.62*tc)/(243.12+tc)
            gamma = math.log((rh/100)*math.exp((18.678-tc/234.5)*tc/(257.14+tc)))
            dp = 257.14*gamma/(18.678-gamma)
            #dp = 243.12*h/(17.62-h)
            dewpointf=dp*(9.0/5.0) +32.0
            drainin=(float(d['rain_mm_day'])/10.0)/2.54
            rainin=(acumulado_lluvia_hora/10.0)/2.54
            #'&rainin='+str(rainin)+
            url_wu = url_1 + '&dateutc=now&tempf='+str(float(d['temperature'])*(9.0/5.0)+32.0) +'&humidity='+ d['humidity'] +'&windspeedmph='+str(float(d['wind_speed'])/1.60934)+'&winddir='+d['wind_direction']
            url_wu = url_wu +'&dailyrainin='+str(drainin)
            url_wu = url_wu +'&rainin='+str(rainin)
            url_wu_2 = url_wu + '&dewptf='+str(round(dewpointf,3))
            print(url_wu_2)
            dif_secs = -1
            with con:
                cur = con.cursor()
                cur.execute("SELECT timestamp, valor FROM status WHERE medicion='pressure'")
                actuales = cur.fetchall()
                local_s = actuales[0][0]
                ts_local = datetime.datetime.strptime(local_s, "%Y-%m-%d %H:%M:%S")
                ts_utc = datetime.datetime.utcfromtimestamp(time.mktime(ts_local.timetuple()))
                medicion_inHg = float(actuales[0][1])/33.863887
                print(ts_local)
                #print(str(ts_utc))
                #print(str(ts_utc.time()))
                date_rep = str(ts_utc.date())
                time_rep = str(ts_utc.time())
                time_rep_2 = re.sub(":","%3A", time_rep)
                time_fin = date_rep+"+"+time_rep_2
                #print(time_fin)
                dif_secs=-(ts_local-datetime.datetime.now()).total_seconds()
                #print(actuales[0][1])
                print(medicion_inHg)
                print(dif_secs)
                #req_bar = url_1+'&dateutc='+time_fin+'&baromin='+str(medicion_inHg)
                #print(req_bar)
                #time.sleep(4)
            
            if(dif_secs < 60*10 and dif_secs>0):
                url_wu_2 = url_wu_2 + '&baromin='+str(medicion_inHg)
            print(url_wu_2)
            q = requests.get(url_wu_2, timeout=10)  
            print(q.status_code)
 
                #q2 = requests.get(url_1+'&dateutc='+time_fin+'&baromin='+str(medicion_inHg))
                #print q2.status_code

        except:
            print("Error wunderground.")
    except:
        print("Error request--")
        logging.error('Error request')
        time.sleep(10)
    
        
        
    #dweepy.dweet_for('rich-honey', {'wind_speed':str(reading_ws), 
    #   'temperature':str(reading_temp), 'rainfall':str(reading_rf), 'wind_direction':str(reading_vane)})
    #print(reading_ws)

    time.sleep(2)

