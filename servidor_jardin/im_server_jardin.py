# -*- coding: utf-8 -*-
import cherrypy
import os, os.path
import picamera
import datetime as dt
from xbee import ZigBee
from cherrypy.process.plugins import Monitor
import serial
from collections import deque
import simplejson
import time
from fractions import Fraction

smooth_ph = 6.0
ph_serie = deque([6.0]*600)
ts_serie = deque(['']*600)
flow_serie =  deque([0.0]*600)
smooth_flow = 20
ultima_foto = dt.datetime.now()
ts=''
x= 'hello'

serial_con = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
xbee = ZigBee(serial_con)

def tomar_foto_baja():
	global ultima_foto
	ahora = dt.datetime.now()
	dif = (ahora-ultima_foto).total_seconds()
	if(dif > 120):
		ultima_foto = ahora
		with picamera.PiCamera() as camera:
			camera.resolution = (320,320)
			#if(hora < 4 or hora > 20):
			#		camera.framerate = Fraction(1, 6)
			#	camera.shutter_speed = 6000000
			#	camera.exposure_mode = 'off'
			#	camera.iso = 800
			#else:
			camera.exposure_mode ='auto'
			camera.annotate_text_size =16
			camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			#camera.vflip = True
			#camera.hflip=True
			camera.rotation=180
			camera.capture('./img/sshot_baja.jpg')

def increment():
	ph_data = 'No reading'
	global smooth_ph
	global smooth_flow
	global ts
	global ph_serie
	global flow_serie
	global xbee

	frame = xbee.wait_read_frame(timeout=0.5)
	print frame
	
	if('rf_data' in frame.keys()):
		split_frame = frame['rf_data'].split('\n')
		ph_data = float(split_frame[1].split(',')[3])
		flow_data = float(split_frame[2].split(',')[3])
		ts = str(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		smooth_ph = smooth_ph*0.6 + 0.4*ph_data
		smooth_flow = smooth_flow*0.6 + 0.4*flow_data
		temp = ph_serie.popleft()
		ph_serie.append(round(smooth_ph, 2))
		flow_serie.append(round(smooth_flow/7.5,2))
		temp = ts_serie.popleft()
		temp = flow_serie.popleft()
		ts_serie.append(ts)
	

Monitor(cherrypy.engine, increment, frequency =2).subscribe()

class JardinApp(object):
	@cherrypy.expose
	def monitor(self):
		return file('index.html')
	
	@cherrypy.expose
	def cuerpo(self):
		global smooth_ph
		global smooth_flow
		global ts
		global ph_serie
		#tomar_foto_baja()
		out_html = ""
		out_html = out_html + "<p>Acceso en "+ts + "</p>  <p> pH: " + str(round(smooth_ph,1)) + ", flujo: " + str(int(smooth_flow))
		#out_html = out_html + '<img src="/img/sshot_baja.jpg" class="img-responsive center-block">'
		#out_html = out_html + str(list(ph_serie))
		out_html = out_html + "</p>"
		return out_html
	
	@cherrypy.expose
	def imagen(self):
		tomar_foto_baja()
		return '<img src="/img/sshot_baja.jpg" class="img-reponsive center-block">'
	@cherrypy.expose
	def dat_ph(self):
		global ph_serie
#		cherrypy.response.headers['Content-Type'] = 'application/json'
		return simplejson.dumps(dict(data_ph=list(ph_serie), time=list(ts_serie),data_flow=list(flow_serie)))
        
	@cherrypy.expose
        def camara_alta(self):
                with picamera.PiCamera() as camera:
                        camera.resolution = (2592,1944)
			camera.exposure_mode ='auto'
                        camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			#camera.vflip = True
			#camera.hflip=True
    			#camera.rotation=90
                   	camera.capture('./img/sshot.jpg')
                return """<html>
                        <head></head>
                        <body> 
                        <img src="/img/sshot.jpg" alt="some_text">
                        </body>
                        </html>"""

if __name__=='__main__':
        cherrypy.config.update({'server.socket_host': '0.0.0.0'} )

        conf = {
		'/':{'tools.sessions.on':True,'tools.staticdir.root':os.path.abspath(os.getcwd())},
                '/img':{'tools.staticdir.on':True,'tools.staticdir.dir':'./img'},
		'/src':{'tools.staticdir.on':True,'tools.staticdir.dir':'./src'}}
        cherrypy.quickstart(JardinApp(),'/', conf)


