#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xbee import ZigBee
from pushover import Client
#from pushbullet import PushBullet
from os import system
import sqlite3 as lite
import sys
import datetime
import pytz
import serial 
import requests
import json
import time
import math
import io
import os
import sys
import subprocess
from soco import SoCo
from say import text2mp3 
import dweepy
#import Adafruit_BBIO.GPIO as GPIO
import MySQLdb 

tzone = pytz.timezone('America/Mexico_City')
## Definir xbees, luces
lugares = ['escalera','sala','tv','puerta','estudiof','vestidor','cocina','cuarto']

myxbees = {
    '0013a20040bf05de':'escalera', 
    '0013a20040bf0582':'sala',
    '0013a20040c4190d':'tv',
    '0013a20040bef84d':'puerta',
    '0013a20040bf06d4':'estudiof',
    '0013a20040bf962c':'vestidor',
    '0013a20040bf06bd':'cocina',
    '0013a20040c45639':'cuarto'
    }


#mapeo de xbee pins )para cajas sin arduino)
xbee_pin ={'puerta':{'dio-1':'pir', 'dio-2':'puerta', 'adc-3':'photo','dio-4':'cerrar','dio-0':'abrir'},
        'escalera':{'dio-4':'pir'}}

ip_hue ="http://192.168.100.2/api/newdeveloper/"
payoff = json.dumps({"on":False})
payon = json.dumps({"on":True, "bri":255})

ip_sonos = "192.168.100.13" ## ip de bocina play 1 (puede cambiar) TODO
PATH ='/Volumes/mmshared/sonidos'
path_s ='//homeserver/mmshared/sonidos/'
ALERT = 'alert4.mp3' 
LANGUAGE = 'es' # speech language
texto_1 = "Iniciando sistema"
sonos = SoCo(ip_sonos)

ip_felipe = '192.168.100.6'
ip_tere = '192.168.100.7'

# que luces corresponden a cada lugar
luces = {'escalera':[6], 'sala':[3,4,5], 'tv':[1],'puerta':[7],'estudiof':[2],'vestidor':[8],'cocina':[10],'cuarto':[11]}
nivel_encendido= {'escalera':2000,'sala':300, 'tv':300, 'puerta':300,'estudiof':730,'vestidor':900,'cocina':500,'cuarto':600}
delay_luces_l = {'tv':6*60, 'sala':4*60, 'puerta':60, 'escalera':40, 'estudiof':4*60,'vestidor':4*60,
    'cocina':3*60,'cuarto':5*60}

# los que tienen cero envían datos según pausas
delay_registro = {'escalera':1, 'sala':1, 'tv':1, 'estudiof':1, 'puerta':10, 'vestidor':1, 'cocina':1,'cuarto':1}

# inicializar
estado_luces={}
movimiento={}
niveles_luz={}
tiempo_movimiento={}
dormir = {}
movimiento_st={}
for lugar in lugares:
    estado_luces[lugar] = False
    movimiento[lugar] = False
    niveles_luz[lugar] = 1000
    tiempo_movimiento[lugar] = 0
    dormir[lugar] = False

anterior = time.time()


temperaturas = {'sala':0.0, 'tv':0.0,  'estudiof':0.0,'cocina':0.0,'cuarto':0.0}
gas = {'cocina':0.0, 'cuarto':0.0}
puertas = {'puerta':1, 'estudiof':1}
# atributos globales de la casa, alarma enviasa es un flag si ya mandó mensaje
globales = {'activo':True, 'alarma':False, 'alarma_enviada':False, 'alarma_trip':False,
    'ac_encendido':False, 'felipe':True, 'tere':False,
    'alarma_gas':False, 'alarma_gas_enviada':False,'chapa':False}

#xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='D4',parameter='\x05')

SERIAL_PORT = '/dev/tty.usbserial-AH02VCE9'

#conrds = MySQLdb.connect(host="fgdbinstances.cqgwstytvlnn.us-east-1.rds.amazonaws.com", port =3306,
#    user="felipe",passwd="valqui2312",db="dbmonitor")
#con = lite.connect('test.db')
con2 = lite.connect('/Volumes/mmshared/bdatos/ultimas.db')
concom = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
conlocal = lite.connect('/Volumes/mmshared/bdatos/temp_monitor.db')
conrds = MySQLdb.connect(host='localhost', user = 'felipe', db='casa')


def monitorCasa():
    #pb = PushBullet('v1PIC2OwXdaK1aw49OTrNflD3jlpZZdrpPujy4CMcLNi8')
    po_client = Client("upTSkha71ovvG3Q3KSp68VAZRUwx4h", api_token="aeWBgVcie7cwVm2UrWFsTUa52XdezD")
    #po_client_tere = Client("uF7p3ueWbwbhD9c8xer4QLukbWoppT", api_token="")

    #resetear alarma
    globales['alarma'] = False
    globales['alarma_trip'] = False
    globales['alarma_enviada'] = False

    globales['activo'] = True
   
    tocar('iniciar.mp3')

    
    for key in luces:
        apagarGrupo(luces[key])
        estado_luces[key] = False
        print "Luces activas, apagadas " + key
    
    #limpiar comandos pendientes
    with concom:
        c = concom.cursor()
        c.execute('DELETE FROM pendientes') 

    #iniciar conteos
    tiempo_sonos = time.time()
    time_loop = time.time() 
    log_time = time.time()
    dweepy_time = time.time()
    dweepy_time_2 = time.time()
    felipe_phone_time = time.time()

    tiempos_registro = {}
    mom_registrar = {}
    for lugar in lugares:
        tiempos_registro[lugar] = 0
        mom_registrar[lugar] = 0
        movimiento_st[lugar] = 0.0
        estado_luces[lugar] = False
    
    for key in tiempos_registro:
        tiempos_registro[key] = time.time()
    for key in mom_registrar:
        mom_registrar[key] = time.time()
    


    # xbees iniciar conección
    try:
        serialConnection = serial.Serial( SERIAL_PORT, 9600,timeout=0.15)
        xbee = ZigBee(serialConnection)
        print "Conexión xbee serial...OK"
    except:
        print "Error serial/xbee"

    tstamp = time.time()

    anterior = time.time()
    #################### ciclo de monitoreo #########################

    while True:
        #tstamp del ciclo
        #print tstamp - time.time()
        tstamp = time.time()
        dt = datetime.datetime.fromtimestamp(tstamp, tz=tzone)
         # apagar si no se ha detectado movimiento en un rato
        for key in tiempo_movimiento:
            if((tstamp - tiempo_movimiento[key] ) >= delay_luces_l[key]):
                if(globales['activo'] and estado_luces[key]):
                    apagarGrupo(luces[key])
                    estado_luces[key] = False

        ##en inicio todos los movimientos son falsos
        for lugar in lugares:
            movimiento[lugar] = False

        ## leer xbee y procesar ############################
        response = xbee.wait_read_frame(timeout=0.15)

        #if(len(response)>0):
        #    print(response)
        if('source_addr_long' in response.keys()):
            source = response['source_addr_long'].encode('hex')
            lugar = myxbees[source]
            print "***** " + lugar
            #if(lugar=='cuarto'):
            #    print(lugar)
            #    print(response)
            #    print('--------')
            st = datetime.datetime.fromtimestamp(tstamp, tz=tzone).strftime('%Y-%m-%d %H:%M:%S')
            if('rf_data' in response.keys()):
                ocurrencia = procesar_rf(response, st) ## datos de arduino
            if('samples' in response.keys()):
                ocurrencia = procesar_samples_unif(response, st) # datos de xbee sin arduino
                #print ocurrencia
                #print procesar_samples_unif(response, st)
           
            #if(lugar=='cuarto'):
            #    print(ocurrencia)
            # niveles de luz y movimiento, puertas
            #print(ocurrencia)
            for item in ocurrencia:
                if(len(item)>6): ## evitar mesnajes de error de xbees
                    sensor_i = item[3]
                    lugar_i = item[2]
                    valor_i = item[6]
                    ## actualizar lecturas de luz
                    if(sensor_i == 'photo'):
                        try:
                            niveles_luz[lugar_i] = float(valor_i)
                        except:
                            print "Error float luz"
                    # actualizar movimiento
                    if(sensor_i == 'pir'):
                        mov = movimiento[lugar_i]
                        movimiento[lugar_i] = (valor_i=='1') or mov ## para más de un pir en un mismo lugar
                    if(sensor_i== 'lev_snd'):  ## por el momento, el sonido está en el vector movimiento.
                        print 'sonido_env: '+valor_i
                        if(float(valor_i) > 10):
                            movimiento[lugar_i] = True
                            print "Sonido"
                    ## reed switches
                    if(sensor_i=='puerta' and valor_i=='0'):
                        puertas[lugar_i] = 0
                        if(tstamp-tiempo_sonos > 15):
                            tiempo_sonos=time.time()
                            if(not  globales['alarma']):
                                tocar("doorbell.mp3")
                            else:
                                tiempo_sonos=time.time() + 120
                                globales['alarma_trip'] = True
                                tocar("conversa.mp3") ## tocar cuando hay alarma
                    if(sensor_i=='puerta' and valor_i=='1'):
                        puertas[lugar_i] = 1
                    ## temperaturas
                    if(sensor_i=='temperature'):
                        if(temperaturas[lugar_i] > 0):
                            #promediar temps porque algunas cajas tienen 2 sensores
                            temperaturas[lugar_i] = (float(item[6]) + temperaturas[lugar_i])/2 
                        else:
                            temperaturas[lugar_i] = float(item[6])
                    ## checar gas
                    if(sensor_i =='gaslpg'):
                        gas[lugar_i] = valor_i
                        if(float(valor_i) > 400):
                            globales['alarma_gas'] = True
                            lugar_gas = lugar_i
                            lectura = valor_i
  

        ######### luces ########
        # encender luces donde haya movimiento, si están apagadas?
        for key in movimiento:
            if(movimiento[key]):
                tiempo_movimiento[key] = time.time()
                if(niveles_luz[key] < nivel_encendido[key]):
                    if(globales['activo'] and (not dormir[key])):
                        encenderGrupo(luces[key])
                        estado_luces[key] = True

        
        delta = time.time() - anterior
        #print delta
        for key in lugares:
            movimiento_st[key] = max(float(movimiento[key]),movimiento_st[key]*math.exp(-0.01*delta))  


        if(time.time() - dweepy_time > 12):
            dweepy_time = time.time()
            print "registro dwepp2"
            mov_send = {}
            for lugar in lugares:
                mov_send[lugar] = str(round(movimiento_st[lugar],2))
            print mov_send
            try:
                dweepy.dweet_for('well-groomed-move',mov_send)
            except:
                print "error dweepy"
            
            gas_send = {}
            for key in gas:
                gas_send[key] = str(gas[key])
            try:
                dweepy.dweet_for('cynical-powder',gas_send)
                dweepy.dweet_for('fierce-cup',puertas)
            except:
                print "error dweepy"
           
        anterior = time.time()
        if(time.time() - dweepy_time_2 > 15):
            print "registro dw"
            dweepy_time_2 = time.time()
            temp_send = {}
            for key in temperaturas:
                temp_send[key] = str(round(temperaturas[key], 2))
            dweepy.dweet_for('zany-stomach',temp_send)
            luz_send = {}
            for key in niveles_luz:
                luz_send[key] =str(niveles_luz[key])
            
            glob_send={}
            for key in globales:
                glob_send[key] = str(int(globales[key]))
            try:
                dweepy.dweet_for('kindly-police',luz_send) 
                dweepy.dweet_for('pretty-instrument',glob_send)
            except:
                print "error dweepy"


        ########## alarmas #########
        ## alertar por mensaje si alarma
        if(globales['alarma_trip'] and not(globales['alarma_enviada'])):
            encenderGrupo(luces['puerta'])
            try:
                po_client.send_message("Alarma disparada", title="Alarma entrada")
                globales['alarma_enviada'] = True
            except: 
                print "error envio"
                globales['alarma_enviada'] = True
     
        if(globales['alarma_gas'] and not(globales['alarma_gas_enviada'])):
            po_client.send_message("Alarma de gas en "+lugar_gas+", lectura: " + lectura, title="Alarma gas")
            globales['alarma_gas_enviada'] = True
            try:
                sonos.volume = 90
                decir('Alarma de gas en ' + lugar_gas)
                time.sleep(8)
                decir('Alarma de gas en ' + lugar_gas)
                sonos.volume = 40
            except:
                print "Error decir alarma de gas"


        ############ temperatura #########
        # activar aire si temperatura en tv es alta y hay alguien presente
        if(globales['activo'] and temperaturas['tv'] >= 23 and (not globales['ac_encendido'])):
            if(movimiento_st['estudiof'] > 0.01):
                xbee.tx(dest_addr_long='\x00\x13\xa2\x00\x40\xbf\x96\x2c',dest_addr='\x40\xb3', data=b'1')
                
                globales['ac_encendido'] = True
        if(temperaturas['tv'] < 22 and globales['ac_encendido']):
            xbee.tx(dest_addr_long='\x00\x13\xa2\x00\x40\xbf\x96\x2c',dest_addr='\x40\xb3', data=b'1')
            globales['ac_encendido'] = False

      
           
        # procesar comandos pendientes
        with concom:
            c = concom.cursor()
            c.execute('SELECT * FROM pendientes')
            actuales = c.fetchall()
            #print actuales
            for comando in actuales:
                #print comando
                if(comando[0]=='aire_acondicionado'):
                    print "Aire acondicionado"
                    xbee.tx(dest_addr_long='\x00\x13\xa2\x00\x40\xbf\x96\x2c',dest_addr='\x40\xb3', data=b'1')
                    globales['ac_encendido'] = not globales['ac_encendido']
                if(comando[0]=='apagar_luces'):
                    apagarTodas(luces)
                    print "Apagando luces"
                if(comando[0]=='abrir_garage'):
                    print "Abriendo garage"
                    try:
                        r = requests.post('http://192.168.100.19:8090/garage')
                    except:
                        print "Error: Garage no disponible"
                if(comando[0]=='activar_alarma'):
                    if(comando[1]=='1'):
                        globales['alarma'] = True
                        globales['alarma_enviada'] = False
                        globales['alarma_trip'] = False
                        tocar("alarma_activada.mp3")
                        chapa(True, xbee = xbee)
                        for key in luces:
                            apagarGrupo(luces[key])
                        globales['activo'] = False
                    if(comando[1]=='0'):
                        globales['alarma'] = False
                        tocar("alarma_desactivada.mp3")
                        chapa(False, xbee=xbee)
                        globales['alarma_trip']= False
                        globales['alarma_enviada'] = False
                        globales['activo'] = True
                        globales['alarma_gas'] = False
                        globales['alarma_gas_enviada'] = False
                if(comando[0]=='dormir'):
                    dormir['cuarto'] = not dormir['cuarto']
                    if(dormir['cuarto']):
                        decir('Listo para dormir')
                        apagarGrupo(luces['cuarto'])
                        chapa(True, xbee = xbee)
                    else:
                        decir('Hora de despertar')

                if(comando[0]=='chapa' and comando[1]=='1'):
                    print "Cerrar chapa"
                    chapa(True, xbee = xbee)
                if(comando[0]=='chapa' and comando[1]=='0'):
                    print "Abrir chapa"
                    chapa(False, xbee = xbee)
                if(comando[0]=='mantener_luces'):
                    globales['activo'] = not globales['activo']
                    try:
                        with con2:
                            cur2 = con2.cursor()
                            command1 = "UPDATE status SET valor ="+int(activo)+" WHERE lugar='global' AND medicion= 'activo' AND no_sensor=1"
                            command2 = "UPDATE status SET timestamp ="+str(st)+" WHERE lugar='global' AND medicion= 'activo' AND no_sensor=1"
                            cur2.execute(command1)
                            cur2.execute(command2)
                    except:
                        print "Error activo escribir"
            c.execute('DELETE FROM pendientes')
            

        ## actividades programadas
        if(dormir['cuarto'] and dt.hour==8):
            decir('Hora de despertar para Teresita y Felipe')
            dormir['cuarto'] = False


        ## pings
        if(time.time() - felipe_phone_time > 10):
            felipe_iphone = subprocess.call('ping -q -c1 -W 1 '+ '192.168.100.6' + ' > /dev/null', shell=True)
            tere_iphone = subprocess.call('ping -q -c1 -W 1 '+ '192.168.100.7' + ' > /dev/null', shell=True)
            felipe_phone_time = time.time()
            if(felipe_iphone==0):
                globales['felipe'] = True
            else:
                globales['felipe'] = False
            if(tere_iphone==0):
                globales['tere'] = True
            else:
                globales['tere'] = False


        ### registrar sensores
        #try:
        #if(time.time()-mom_registrar[lugar] > delay_registro[lugar]):
        #    mom_registrar[lugar] = time.time()
        #    #print ocurrencia
        #    if 'ocurrencia' in locals():
        #        for item in ocurrencia:
        #            #print(item)
        #            update_ultimas(item, con2, str(st))
        #except:
        #    print("error registro ultimas")


        ## i el lugar le toca registro, actualizar base de datos
        if 'lugar' in locals() and 'ocurrencia' in locals():
            if((time.time() - tiempos_registro[lugar]) > delay_registro[lugar]):
                tiempos_registro[lugar] = time.time()
                #try:
                escribir_ocurrencia_mysql(ocurrencia, conrds)
                #except:
                #    print "Error escribir base completa"
     
        # datos estados en consola    
        if((time.time()-log_time) > 5):
            print '---------------------'
            print 'tiempo loop', time.time()- tstamp
            time_loop = time.time()
            log_time = time.time()
            print "Luz, ", niveles_luz
            print "Temperatura, ", temperaturas
            print "Movimiento, ", movimiento
            print "Mov st ", movimiento_st



            
##############################################################################
        

def escribir_ocurrencia_mysql(ocurrencia, conrds):
    try:
        with conrds:
            for item in ocurrencia:
                if(len(item) > 6):
                    cur = conrds.cursor()
                    comand_base = 'insert into mediciones (tiempo_reg, xbee, lugar, tipo, unidad, num_sensor, valor) VALUES '
                    comand_2 ="('"+item[0]+"','"+item[1]+"','"+item[2]+"','"+item[3]+"','"+item[4]+"','"+str(int(item[5]))+"',"+str(float(item[6]))+")"
                    commandx = comand_base+comand_2
                    cur.execute(commandx)
    except:
        print "Error escribir_ocurrencia_mysql"


def procesar_rf(response, st):
    ocurrencias = []
    source = response['source_addr_long'].encode('hex')
    lugar = myxbees[source]
    lecturas = response['rf_data'].split('\r\n')
    for item in lecturas:
        lecs = item.split(',')
        lecs.insert(0, lugar)
        lecs.insert(0, source)
        lecs.insert(0, st)
        if(len(lecs) > 4):
            ocurrencias.append(lecs)
    return ocurrencias
        

def procesar_samples_unif(response, st):
    ocurrencias = []
    source = response['source_addr_long'].encode('hex')
    lugar = myxbees[source]
    lecturas = response['samples']

    #xbee_pin[lugar][key], tipo binary, 1
    #convertir 
    for elem in lecturas:
        for key in elem:
            if (key[0:3] == 'adc'):
                tipo = 'analog'
                temp_val = elem[key]
            else:
                tipo = 'binary'
                if(elem[key]==True):
                    temp_val ='1'
                else:
                    temp_val='0'

            salida = [st, source, lugar,(xbee_pin[lugar])[key],tipo,'1',temp_val]
            ocurrencias.append(salida)
    return ocurrencias


def apagarGrupo(grupo):
   for luz in grupo:
        try:
            r = requests.put(ip_hue + 'lights/'+str(luz)+'/state', data=payoff, timeout=0.1)
        except:
            print "Luces no disponibles para apagar"
def encenderGrupo(grupo):
   for luz in grupo:
        try:
            r = requests.put(ip_hue + 'lights/'+str(luz)+'/state', data=payon, timeout=0.3)
        except:
            print "Luces no disponibles para encender"

def apagarTodas(luces):
    for zona in luces:
        apagarGrupo(luces[zona])

def chapa(cerrar, xbee):
    if(cerrar):
        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='D4',parameter='\x05')
        time.sleep(0.2)
        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='D4',parameter='\x04')
        globales['chapa'] = True
    else:
        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='D0',parameter='\x05')
        time.sleep(0.2)
        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='D0',parameter='\x04')
        globales['chapa'] = False



def update_ultimas(item, con2, ts):
    try:
        with con2:
            cur2 = con2.cursor()
            valbase = item[6]
            if(isinstance(item[6], bool)):
                valbase = float(item[6])
            command1 = "UPDATE status SET valor ="+str(valbase)+" WHERE lugar='"+item[2]+"' AND medicion= '"+item[3]+"' AND no_sensor="+str(item[5])
            command2 = "UPDATE status SET timestamp ='" +ts+"' WHERE lugar='"+item[2]+"' AND medicion= '"+item[3]+"' AND no_sensor="+str(item[5])

        #print command1
        #print command2
            cur2.execute(command1)
            cur2.execute(command2)
    except:
        #print command1
        #print command2
        print "Error sqlite ultimas"

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)         
        
def tocar(archivo):
    try:
        #track = sonos.get_current_track_info()
        #playlistPos = int(track['playlist_position'])-1
        #trackPos = track['position']
        #trackURI = track['uri']

    # This information allows us to resume services like Pandora
        #mediaInfo = sonos.avTransport.GetMediaInfo([('InstanceID', 0)])
        #mediaURI = mediaInfo['CurrentURI']
        #mediaMeta = mediaInfo['CurrentURIMetaData']

        sonos.play_uri('x-file-cifs://homeserver/sonidos/'+archivo)
        #sleepTime=2
        #time.sleep(sleepTime)
        #if len(zp.get_queue()) > 0 and playlistPos > 0:
        #    print 'Resume queue from %d: %s - %s' % (playlistPos, track['artist'], track['title'])
        #    sonos.play_from_queue(playlistPos)
        #    sonos.seek(trackPos)
        #else:
        #    print 'Resuming %s' % mediaURI
        #    sonos.play_uri(mediaURI, mediaMeta)


    except:
        print "Error sonos"


def decir(texto):
    track = sonos.get_current_track_info()
    playlistPos = int(track['playlist_position'])-1
    trackPos = track['position']
    trackURI = track['uri']

    # This information allows us to resume services like Pandora
    mediaInfo = sonos.avTransport.GetMediaInfo([('InstanceID', 0)])
    mediaURI = mediaInfo['CurrentURI']
    mediaMeta = mediaInfo['CurrentURIMetaData']

    # Play the alert sound, and sleep to allow it to play through
    #print 'Playing alert %s' % alertSoundURL
    #sonos.play_uri(alertSoundURL)
    


    ok, file_name =  text2mp3(texto, PATH, LANGUAGE, ALERT)
    if ok:
        zp = SoCo(ip_sonos)
        print('x-file-cifs:%s' % '//homeserver/sonidos/speech.mp3')
        zp.play_uri('x-file-cifs:%s' % '//homeserver/sonidos/speech.mp3')
        #alertDuration = zp.get_current_track_info()['duration']
        #sleepTime=float(alertDuration)
        #time.sleep(sleepTime)
        #if len(zp.get_queue()) > 0 and playlistPos > 0:
        #    print 'Resume queue from %d: %s - %s' % (playlistPos, track['artist'], track['title'])
        #    zp.play_from_queue(playlistPos)
        #    zp.seek(trackPos)
        #else:
        #    print 'Resuming %s' % mediaURI
         #   zp.play_uri(mediaURI, mediaMeta)


# if run as top-level script
if __name__ == "__main__":
    try:
        monitorCasa()
    except KeyboardInterrupt:
        #GPIO.output("P8_10", GPIO.LOW)    
        conlocal.close()
        #conrds.close()
        pass
