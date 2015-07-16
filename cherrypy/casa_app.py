import os, os.path
import random
import string
import sqlite3 as lite
import HTML
import cherrypy

cherrypy.server.socket_host = '0.0.0.0'


class control(object):

    @cherrypy.expose
    def controlcasa(self):
        return file('index_main.html')


    @cherrypy.expose
    def autoluz(self):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('auto_luces','0')"
            cur.execute(commandx)
        return 'Auto luces' 

    @cherrypy.expose
    def auto_ac(self):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('auto_ac','0')"
            cur.execute(commandx)
        return 'Auto ac toggle' 

    @cherrypy.expose
    def control_aire(self):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('aire_acondicionado','0')"
            cur.execute(commandx)
        return 'Enviado comando AC'

    @cherrypy.expose
    def garage(self):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('abrir_garage','1')"
            cur.execute(commandx)
        return 'Activando garage'

    @cherrypy.expose
    def alarma(self, sw):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            if(sw=='1'):
                commandx = "INSERT INTO pendientes VALUES('activar_alarma','1')"
                mensaje = 'Activando alarma'
            else:
                commandx = "INSERT INTO pendientes VALUES('activar_alarma','0')"
                mensaje = 'Desactivando alarma'
            cur.execute(commandx)
        return mensaje

    @cherrypy.expose
    def chapa(self, sw):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            if(sw=='1'):
                commandx = "INSERT INTO pendientes VALUES('chapa','1')"
                mensaje ='Cerrar chapa'
            if(sw=='0'):
                commandx = "INSERT INTO pendientes VALUES('chapa','0')"
                mensaje = 'Abrir chapa'
            cur.execute(commandx)
        return mensaje

    @cherrypy.expose
    def regar(self, sw):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            if(sw=='1'):
                commandx = "INSERT INTO pendientes VALUES('regar','1')"
                mensaje ='Regar patio'
            if(sw=='0'):
                commandx = "INSERT INTO pendientes VALUES('regar','0')"
                mensaje = 'Dejar de regar patio'
            cur.execute(commandx)
        return mensaje


    @cherrypy.expose
    def dormir(self):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('dormir','0')"
            cur.execute(commandx)
        return 'Comando dormir'

    @cherrypy.expose
    def zumbador(self):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('puerta_zumbador','1')"
            cur.execute(commandx)
        return 'Zumbando 2s'


    @cherrypy.expose
    def apagar_luces(self):
        con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
        with con:
            cur = con.cursor()
            commandx = "INSERT INTO pendientes VALUES('apagar_luces','0')"
            cur.execute(commandx)
        return 'Apagando luces' 

class infoBasica(object):
    exposed = True
    @cherrypy.tools.accept(media='text/plain')
    def GET(self, resp=''):
        con2 = lite.connect('/Volumes/mmshared/bdatos/ultimas.db')
        with con2:
            cur = con2.cursor()
            commandx = "SELECT timestamp, medicion, valor from Status WHERE lugar = 'global' ORDER BY medicion" # OR (lugar='tv' AND medicion='temperature') "
            #commandx = "SELECT timestamp,medicion,valor,lugar from Status  ORDER BY lugar, medicion "
            res = cur.execute(commandx)
        tabla = HTML.table(res).split('\n')
        tabla2 = " ".join(tabla[1:(len(tabla)-1)])
        tabla3 =  "<table class='table table-striped lead'>"+tabla2+"</table>"
        con2.close()
        return tabla3











# class lucesCocina(object):
#      exposed = True
#      @cherrypy.tools.accept(media='text/plain')
#      def POST(self, resp=''):
#         con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
#         with con:
#             cur = con.cursor()
#             commandx = "INSERT INTO pendientes VALUES('luces_cocina','1')"
#             cur.execute(commandx)
#         return 'Apagando luces' 


# class apagarCocina(object):
#      exposed = True
#      @cherrypy.tools.accept(media='text/plain')
#      def POST(self, resp=''):
#         con = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
#         with con:
#             cur = con.cursor()
#             commandx = "INSERT INTO pendientes VALUES('luces_cocina','0')"
#             cur.execute(commandx)
#         return 'Apagando luces' 




#class estadoSys(object):
#    exposed = True
#    @cherrypy.tools.accept(media='text/plain')

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port':8090})
    conf = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': os.path.abspath(os.getcwd())
         },
         '/info_bas': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },

         '/dist/css/bootstrap.min.css': {
		'tools.staticfile.on' : True,
		'tools.staticfile.filename' : "/Users/felipe/servidor_casa/cherrypy/dist/css/bootstrap.min.css"
        },
        '/dist/jquery/jquery-2.0.3.min.js': {
        'tools.staticfile.on' : True,
        'tools.staticfile.filename' : "/Users/felipe/servidor_casa/cherrypy/dist/jquery/jquery-2.0.3.min.js"
        },
        '/dist/app.js':{
            'tools.staticfile.on' : True,
            'tools.staticfile.filename' : "/Users/felipe/servidor_casa/cherrypy/dist/app.js"
        },
        '/img':{
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : "/Users/felipe/servidor_casa/cherrypy/img"
        }
}
    webapp = control()
    webapp.info_bas = infoBasica()

    cherrypy.quickstart(webapp, '/', conf)

