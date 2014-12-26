import os, os.path
import random
import string
import sqlite3 as lite
import HTML
import cherrypy

cherrypy.server.socket_host = '0.0.0.0'


class control(object):
    @cherrypy.expose
    def index(self):
        return file('index.html')

    @cherrypy.expose
    def controlcasa(self):
        return file('index_garage.html')

    @cherrypy.expose
    def reportar(self):
        con = lite.connect('/Volumes/mmshared/bdatos/ultimas.db')
        with con:
            cur = con.cursor()
            commandx = "SELECT * from Status ORDER BY medicion, lugar"
            cur.execute(commandx)
            res = cur.fetchall()
            tabla = '<!DOCTYPE html><html><head><script src="http://code.jquery.com/jquery-2.0.3.min.js"></script><link href="/dist/css/bootstrap.min.css" rel="stylesheet"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body>'+'<h2>Monitores</h2><table class="table table-condensed">'+HTML.table(res)+'</table></body></html>'
        return tabla


class controlGarage(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
  
    def POST(self, resp=''):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('abrir_garage','1')"
            cur.execute(commandx)
        return 'Activando garage'
class controlAlarma(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
  
    def POST(self, resp=''):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('activar_alarma','1')"
            cur.execute(commandx)
        return 'Activando alarma'

class desAlarma(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
  
    def POST(self, resp=''):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('activar_alarma','0')"
            cur.execute(commandx)
        return 'Desactivando alarma'
class controlAire(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
  
    def POST(self, resp=''):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('aire_acondicionado','0')"
            cur.execute(commandx)
        return 'Enviado comando AC'




class controlPausa(object):
     exposed = True

     @cherrypy.tools.accept(media='text/plain')
  
     def POST(self, resp=''):
         print "Pausando algunas cosas"
         return 'cambiar pausa'  


class apagarLuces(object):
     exposed = True
     @cherrypy.tools.accept(media='text/plain')
     def POST(self, resp=''):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('apagar_luces','0')"
            cur.execute(commandx)
        return 'Apagando luces' 


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port':8090})
    conf = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': os.path.abspath(os.getcwd())
         },
         '/garage': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         '/alarma': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         '/alarma_des': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         '/control_aire': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         '/apagar_luces': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         '/pausa': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         '/dist/css/bootstrap.min.css': {
		'tools.staticfile.on' : True,
		'tools.staticfile.filename' : "/Users/felipe/casa_servidor/cherrypy/dist/css/bootstrap.min.css"
     }
}
    webapp = control()
    webapp.garage= controlGarage()
    webapp.pausa = controlPausa()
    webapp.alarma = controlAlarma()
    webapp.alarma_des = desAlarma()
    webapp.control_aire = controlAire()
    webapp.apagar_luces = apagarLuces()
    cherrypy.quickstart(webapp, '/', conf)

