import cherrypy
import os, os.path
import picamera
import datetime as dt
#camera=picamera.PiCamera()
#camera.resolution = (640,480)
#camera.exposure_mode ='auto'
class Hello(object):
	@cherrypy.expose
	def index(self):
		with picamera.PiCamera() as camera:
			camera.resolution = (640,480)
			camera.exposure_mode ='auto'
			#camera.annotate_background = picamera.color('black')
			camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			#camera.led = False
			camera.capture('./img/sshot.jpg')
			#camera.exposure_mode='night'
			#camera.capture('./img/sshot_n.jpg')
		return """<html>
			<head></head>
			<body> 
			<img src="/img/sshot.jpg" alt="some_text">
			</body>
			</html>"""

if __name__=='__main__':
	cherrypy.config.update({'server.socket_host': '0.0.0.0'} )
	
	conf = {'/':{'tools.sessions.on':True,'tools.staticdir.root':os.path.abspath(os.getcwd())},
		'/img':{'tools.staticdir.on':True,'tools.staticdir.dir':'./img'}}      
	cherrypy.quickstart(Hello(),'/', conf)
