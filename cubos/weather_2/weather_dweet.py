import dweepy
import requests
import time
import json
import phant
import logging
import logging.handlers

## logging
format_logging = logging.Formatter(fmt='%(levelname)s:%(asctime)s:%(name)s: %(message)s ', datefmt="%Y-%m-%d %H:%M:%S")
h = logging.handlers.TimedRotatingFileHandler('/Volumes/mmshared/bdatos/log/monitor/estacion_meteo.log', encoding='utf8',
        interval=1, when='D', backupCount=1)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
h.setFormatter(format_logging)
h.setLevel(logging.DEBUG)
root_logger.addHandler(h)

p = phant.Phant("XGvXXOnn1aFKYpJGvV6r", 'temperature','humidity',
	'wind_direction','wind_speed','rain_mm_day',private_key = "1J0ggV88qKtMbqDnN64x")
while(True):
	try:
		r = requests.get('http://meteoyun.local/arduino/weather/0')
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

		#try:
			#p.log(d['temperature'],d['humidity'],d['wind_direction'],d['wind_speed'],d['rain_mm_day'])
			#print(p.remaining_bytes, p.cap)
		#except:
			#print("Error sparkfun.")
	except:
		print("Error request--")
		logging.error('Error request')
		time.sleep(5)
	
        
        
	#dweepy.dweet_for('rich-honey', {'wind_speed':str(reading_ws), 
	#	'temperature':str(reading_temp), 'rainfall':str(reading_rf), 'wind_direction':str(reading_vane)})
	#print(reading_ws)

	time.sleep(2)

