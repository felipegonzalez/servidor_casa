import dweepy
import requests
import time
import json
import phant
import logging
import logging.handlers
import math
## logging
format_logging = logging.Formatter(fmt='%(levelname)s|%(asctime)s|%(name)s| %(message)s ', datefmt="%Y-%m-%d %H:%M:%S")
h = logging.handlers.TimedRotatingFileHandler('/Volumes/mmshared/bdatos/log/monitor/estacion_meteo.log', encoding='utf8',
        interval=1, when='midnight', backupCount=4000)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
h.setFormatter(format_logging)
h.setLevel(logging.DEBUG)
root_logger.addHandler(h)

url_wunder = 'http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?'
id_wunder = 'IDISTRIT49' 
pass_wunder= 'A34-Qg6-272-6Jq'
#http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?ID=KCASANFR5&PASSWORD=XXXXXX&dateutc=2000-01-01+10%3A32%3A35&winddir=230&windspeedmph=12&windgustmph=12&tempf=70&rainin=0&baromin=29.1&dewptf=68.2&humidity=90&weather=&clouds=&softwaretype=vws%20versionxx&action=updateraw
url_1 = url_wunder + 'ID='+id_wunder+'&PASSWORD='+pass_wunder
#p = phant.Phant("XGvXXOnn1aFKYpJGvV6r", 'temperature','humidity',
#	'wind_direction','wind_speed','rain_mm_day',private_key = "1J0ggV88qKtMbqDnN64x")
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
		try:
			rh = float(d['humidity'])
			tc = float(d['temperature'])
			h = (math.log10(rh) -2.0)/0.4343 + (17.62*tc)/(243.12+tc)
			dp = 243.12*h/(17.62-h)
			dewpointf=dp*(9.0/5.0) +32.0
			drainin=(float(d['rain_mm_day'])/10.0)/2.54
			rainin=(float(d['rain_mm_hour'])/10.0)/2.54
			url_wu = url_1 + '&dateutc=now&tempf='+str(float(d['temperature'])*(9.0/5.0)+32.0) +'&humidity='+ d['humidity'] +'&dailyrainin='+str(drainin)+'&rainin='+str(rainin)+'&windspeedmph='+str(float(d['wind_speed'])/1.60934)+'&winddir='+d['wind_direction']
			url_wu_2 = url_wu + '&dewpointf='+str(round(dewpointf,3))
			print(url_wu_2)
			q = requests.get(url_wu_2, timeout=10)
			print(q.status_code)
			#p.log(d['temperature'],d['humidity'],d['wind_direction'],d['wind_speed'],d['rain_mm_day'])
			#print(p.remaining_bytes, p.cap)
		except:
			print("Error wunderground.")
	except:
		print("Error request--")
		logging.error('Error request')
		time.sleep(5)
	
        
        
	#dweepy.dweet_for('rich-honey', {'wind_speed':str(reading_ws), 
	#	'temperature':str(reading_temp), 'rainfall':str(reading_rf), 'wind_direction':str(reading_vane)})
	#print(reading_ws)

	time.sleep(2)

