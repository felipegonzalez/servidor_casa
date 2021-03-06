#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import logging.handlers
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
import soco
from say import text2mp3 
import dweepy
#import Adafruit_BBIO.GPIO as GPIO
import MySQLdb 
import cPickle
from collections import deque
import redis
import os
print os.environ['HOME']

# using get will return `None` if a key is not present rather than raise a `KeyError`
pb_key = os.environ.get('PB_TOKEN')
pb_api_key = os.environ.get('PB_API_TOKEN')


##logging
format_logging = logging.Formatter(fmt='%(levelname)s|%(asctime)s|%(name)s| %(message)s ', datefmt="%Y-%m-%d %H:%M:%S")
h = logging.handlers.TimedRotatingFileHandler('/Volumes/mmshared/bdatos/log/monitor/casa_monitor.log', encoding='utf8',
        interval=1, when='midnight', backupCount=4000)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
h.setFormatter(format_logging)
h.setLevel(logging.DEBUG)
root_logger.addHandler(h)
### end loggig handler
print('Creado logging')
#logging.info('Comienza logging')


tiempos = deque([0.0,0.0,0.0,0.0,0.0])

tzone = pytz.timezone('America/Mexico_City')
## Definir xbees, luces
lugares = ['escalera','sala','tv','puerta','estudiof','vestidor',
'cocina','cuarto','entrada','estudiot','bano_cuarto','bano_escalera','casa','patio']

myxbees = {
    '0013a20040bf05de':'escalera', 
    '0013a20040bf0582':'sala',
    '0013a20040c4190d':'tv',
    '0013a20040bef84d':'puerta',
    '0013a20040bf06d4':'estudiof',
    '0013a20040bf962c':'vestidor',
    '0013a20040bf06bd':'cocina',
    '0013a20040c45639':'cuarto',
    '0013a20040bef862':'cocina_entrada',
    '0013a20040be4592':'estudiot',
    '0013a20040c2833b':'bano_cuarto',
    '0013a20040caaddc':'bano_escalera',
    '0013a20040c46287':'estudiof', ## este es el sensor de aire.
    '0013a20040c4605b':'casa',
    '0013a20040caadda':'patio'
    }

#lugares_xbee = {}
#lugares_xbee['escalera']

lugares_xbees = {}

#mapeo de xbee pins )para cajas sin arduino)
xbee_pin ={'puerta':{'dio-1':'pir', 'dio-2':'puerta', 'adc-3':'photo','dio-4':'cerrar','dio-0':'abrir'},
        'escalera':{'dio-4':'pir'},'bano_cuarto':{'dio-1':'pir'},'bano_escalera':{'dio-1':'pir'}}

ip_hue ="http://192.168.100.29/api/newdeveloper/"
payoff = json.dumps({"on":False})
payon = json.dumps({"on":True, "bri":255})

#ip_sonos = "192.168.100.7" ## ip de bocina play 1 (puede cambiar) TODO
PATH ='/Volumes/mmshared/sonidos'
path_s ='//homeserver/mmshared/sonidos/'
ALERT = 'alert4.mp3' 
LANGUAGE = 'es' # speech language



#sonos = SoCo(ip_sonos)
sonos_lista = soco.discover()

while(len(sonos_lista) > 0):
    zona = sonos_lista.pop()
    if(zona.player_name=='Estudio'):
        sonos = zona
        print "Sonos estudio encontrado"
        break


#ip_felipe = '192.168.100.6'
#ip_tere = '192.168.100.7'

# que luces corresponden a cada lugar
luces = {'escalera':[6], 'sala':[3,4,5], 'tv':[1,18],'puerta':[7,17],
'estudiof':[12],'vestidor':[8],'entrada':[9,10],'cuarto':[11],
'estudiot':[13],'bano_cuarto':[14,15],'bano_escalera':[16],'casa':[], 'patio':[]}
nivel_encendido= {'escalera':2000,'sala':300, 'tv':300, 'puerta':700,'estudiof':730,'vestidor':900,
'cocina':800,'cuarto':600, 'entrada':700,'estudiot':700,'bano_cuarto':500,'bano_escalera':2000}
delay_luces_l = {'tv':6*60, 'sala':4*60, 'puerta':60, 'escalera':40, 'estudiof':4*60,'vestidor':4*60,
    'cocina':3*60,'cuarto':7*60,'entrada':4*60,'estudiot':6*60,'bano_cuarto':3*60,
    'bano_escalera':2*60,'casa':10000000, 'patio':60}

# los que tienen cero envían datos según pausas
delay_registro = {'escalera':60, 'sala':60, 'tv':60, 'estudiof':60, 'puerta':60, 'vestidor':60, 
'cocina':60,'cuarto':60,'entrada':10,'estudiot':60,'bano_cuarto':60,'bano_escalera':60,'casa':60,'patio':60}
delay_pressure = 10
# inicializar
estado_luces={}
movimiento={}
niveles_luz={}
tiempo_movimiento={}
dormir = {}
movimiento_st={}

movimiento_tv_st  = {'1':0, '2':0}
ocupacion = {}

for lugar in lugares:
    estado_luces[lugar] = False
    movimiento[lugar] = False
    niveles_luz[lugar] = 1000
    tiempo_movimiento[lugar] = 0
    dormir[lugar] = False
    ocupacion[lugar] = 0
ocupacion['tv'] = 0

niveles_luz['bano_escalera'] = 0
anterior = time.time()


temperaturas = {'sala':0.0, 'tv':0.0,  'estudiof':0.0,'cocina':0.0,'cuarto':0.0,'estudiot':0.0}
humedades ={'sala':0.0, 'cocina':0.0}
gas = {'cocina':0.0, 'cuarto':0.0}
puertas = {'puerta':1, 'estudiof':1,'estudiot':1}
# atributos globales de la casa, alarma enviasa es un flag si ya mandó mensaje
globales = {'activo':True, 'alarma':False, 'alarma_enviada':False, 'alarma_trip':False,
    'ac_encendido':False, 'auto_ac':True, 'felipe':False, 'tere':False, 
    'alarma_gas':False, 'alarma_gas_enviada':False,'chapa':False,'actividad_entrada':False,
    'auto_luces':True, 'mA':0.0, 'regadora':False}

#xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='D4',parameter='\x05')

SERIAL_PORT = '/dev/tty.usbserial-AH02VCE9'

#conrds = MySQLdb.connect(host="fgdbinstances.cqgwstytvlnn.us-east-1.rds.amazonaws.com", port =3306,
#    user="felipe",passwd="valqui2312",db="dbmonitor")
#con = lite.connect('test.db')
print("Preparar bases de datos....")
con2 = lite.connect('/Volumes/mmshared/bdatos/ultimas.db')
conlocal = lite.connect('/Volumes/mmshared/bdatos/temp_monitor.db')
conrds = MySQLdb.connect(host='localhost', user = 'felipe', db='casa')
con_dweet= lite.connect('/Volumes/mmshared/bdatos/to_dweet.db')
redis_q = redis.Redis()

def monitorCasa():
    print("Iniciando....")
    logging.info('Starting')
    print("conectando pushbullet")

    po_client = Client(pb_key, api_token = pb_api_key)
    previo_no_tv='0'


    #resetear alarma
    globales['alarma'] = False
    globales['alarma_trip'] = False
    globales['alarma_enviada'] = False
    globales['auto_ac'] = False
    globales['activo'] = True
    actualizar_global('auto_ac',0, con2)
    actualizar_global('activo',1.0, con2)
    actualizar_global('auto_luces',1.0, con2)
    actualizar_global('alarma',0, con2)
    actualizar_global('chapa',0, con2)

    chapa_por_cerrar = False

    print("Probando sonos...")
    estado_sonos = tocar('iniciar.mp3')

    print("Apagando luces...")
    for key in luces:
        apagarGrupo(luces[key])
        estado_luces[key] = False
        print "Luces activas, apagadas " + key

    


    #limpiar comandos pendientes
    print("Conectando con bd de comandos...")
    concom = lite.connect('/Volumes/mmshared/bdatos/comandos.db')

    with concom:
        c = concom.cursor()
        c.execute('DELETE FROM pendientes') 
    concom.close()
    #iniciar conteos
    tiempo_comandos= time.time()
    tiempo_sonos = time.time()
    time_loop = time.time() 
    log_time = time.time()
    dweepy_time = time.time()
    dweepy_time_2 = time.time()
    felipe_phone_time = time.time()
    check_lights_time = time.time()
    tiempos_registro = {}
    estado_hue={}
    mom_registrar = {}
    tiempo_encendido={}
    for lugar in lugares:
        tiempos_registro[lugar] = 0
        mom_registrar[lugar] = 0
        movimiento_st[lugar] = 0.0
        estado_luces[lugar] = False
        tiempo_encendido[lugar] = 0

    tiempo_pressure = time.time()
    
    for key in tiempos_registro:
        tiempos_registro[key] = time.time()
    for key in mom_registrar:
        mom_registrar[key] = time.time()
    for key in tiempo_encendido:
        tiempo_encendido[key] = 0
    


    # xbees iniciar conección
    print("Activar xbee coordinator...")
    try:
        serialConnection = serial.Serial( SERIAL_PORT, 9600,timeout=0.15)
        xbee = ZigBee(serialConnection)
        print "Conexión xbee serial...OK"
    except:
        logging.warning('Error serial/xbee')
        print "Error serial/xbee"
    # luces cocina apagadas
    xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8\x62',command='D2',parameter='\x04')
    # zumbador apagado
    xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8\x62',command='D1',parameter='\x04')
    tstamp = time.time()

    anterior = time.time()
    #################### ciclo de monitoreo #########################
    print ("Iniciar ciclo principal...")
    contar_mysql=0
    while True:
        #tstamp del ciclo
        #print tstamp - time.time()

        tstamp = time.time()
        dt = datetime.datetime.fromtimestamp(tstamp, tz=tzone)
         # apagar si no se ha detectado movimiento en un rato
        for key in tiempo_movimiento:
            if((tstamp - tiempo_movimiento[key] ) >= delay_luces_l[key]):
                if(globales['activo'] and estado_luces[key] and globales['auto_luces']):
                    if(key=='cocina'):
                        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8\x62',command='D2',parameter='\x04')
                        #estado_luces[key] = False
                        print("Apagar cocina.")
                    else:
                        if(ocupacion[key]==0):
                            apagarGrupo(luces[key])
                    estado_luces[key] = False
                    



        ##en inicio todos los movimientos son falsos
        for lugar in lugares:
            movimiento[lugar] = False

        ## leer xbee y procesar ############################

        response = xbee.wait_read_frame(timeout=0.15)
        #print(response)

        if('source_addr_long' in response.keys()):
            source = response['source_addr_long'].encode('hex')

            lugar = myxbees[source]
            
            if(lugar=='bano_escalera'):
                print "***** " + lugar
                print(response)

            #if(lugar=='cocina_entrada'):
            #    print(lugar)
            #    print(response)
            #    print('--------')

            st = datetime.datetime.fromtimestamp(tstamp, tz=tzone).strftime('%Y-%m-%d %H:%M:%S')
            if('rf_data' in response.keys()):
                ocurrencia = procesar_rf(response, st) ## datos de arduino
            if('samples' in response.keys()):
                ocurrencia = procesar_samples_unif(response, st) # datos de xbee sin arduino 
            if(lugar=='bano_escalera'):
                print "***** " + lugar
                print(ocurrencia)
                
        #######################################################   
            logging.info('Ocurrencia:'+str(ocurrencia))
            # niveles de luz y movimiento, puertas
          
            for item in ocurrencia:
                if(len(item)>6): ## evitar mesnajes de error de xbees
                    sensor_i = item[3]
                    lugar_i = item[2]
                    valor_i = item[6]
                    ## actualizar lecturas de luz
                    if(sensor_i=='ct'):
                        if(item[4]=='A'):
                            #print "Amperes " + str(valor_i)
                            globales['mA'] = str(int(1000*float(valor_i)))
                            actualizar_global('amperes', float(valor_i), con2)
                        if(item[4]=='kW'):
                            actualizar_global('kW', float(valor_i), con2)
                            globales['W'] = str(int(1000*float(valor_i)))
                    if(sensor_i=='dust_density'):
                        print("***************")
                        print(ocurrencia)
                    if(sensor_i == 'photo'):
                        try:
                            niveles_luz[lugar_i] = float(valor_i)
                            #poner nivel de cuarto a baño de cuarto
                            if(lugar_i=='cuarto'):
                                niveles_luz['bano_cuarto'] = float(valor_i) 
                        except:
                            print "Error float luz"
                    # actualizar movimiento
                    if(sensor_i == 'pir'):
                        movimiento['casa'] == True
                        mov = movimiento[lugar_i]
                        movimiento[lugar_i] = (valor_i=='1') or mov ## para más de un pir en un mismo lugar
                        if(lugar_i=='tv' and valor_i=='1'):
                            no_sensor = item[5]
                            movimiento_tv_st[item[5]] = 1.0
                            if(movimiento_tv_st['2'] > movimiento_tv_st['1']):
                                ocupacion['tv'] = 1
                            if(movimiento_tv_st['1'] > movimiento_tv_st['2']):
                                ocupacion['tv'] = 0
                            #if(movimiento_tv_st['2']==1.0 and movimiento_tv_st['1']>0.99):
                            #    ocupacion['tv'] = ocupacion['tv'] + 1
                            #if(movimiento_tv_st['1']==1.0 and movimiento_tv_st['2']>0.99):
                            #    ocupacion['tv'] = ocupacion['tv'] - 1
                        #print ocupacion
                        #print movimiento_tv_st
                    if(sensor_i== 'lev_snd'):  ## por el momento, el sonido está en el vector movimiento.
                        #print 'sonido_env: '+valor_i
                        if(lugar_i=='cuarto'):
                            if(float(valor_i) > 15):
                                movimiento[lugar_i] = True
                        if(lugar_i=='vestidor'):
                            try:
                                valor_snd = float(valor_i)
                                if(valor_snd > 155.0):
                                    if(not globales['ac_encendido']):
                                        globales['ac_encendido'] = True
                                        actualizar_global('ac', 1.0, con2)
                                else:
                                    if(globales['ac_encendido']):
                                        globales['ac_encendido'] = False
                                        actualizar_global('ac', 0.0, con2)
                                    #
                            except:
                                logging.info('Error sonido')
                            #print "Sonido"
                    ## reed switches
                    if(sensor_i=='puerta' and valor_i=='0'):
                        puertas[lugar_i] = 0
                        if(lugar_i=='puerta'):
                            movimiento['entrada'] = True  
                            globales['chapa'] = False

                        if(tstamp-tiempo_sonos > 15):
                            tiempo_sonos=time.time()
                            if(not  globales['alarma']):
                                estado_sonos = tocar("doorbell.mp3")
                            else:
                                tiempo_sonos=time.time() + 50
                                globales['alarma_trip'] = True
                                sonos.volume = 100
                                estado_sonos = tocar("bs_alarm.mp3") ## tocar cuando hay alarma
                                #sonos.volume = 40
                    if(sensor_i=='puerta' and valor_i=='1'):
                        if(puertas[lugar_i]==0 and lugar=='puerta'):
                            tiempo_cerrar_chapa = time.time()
                            chapa_por_cerrar = True
                        puertas[lugar_i] = 1
                        
                    ## temperaturas
                    if(sensor_i=='temperature'):
                        if(temperaturas[lugar_i] > 0):
                            #promediar temps porque algunas cajas tienen 2 sensores
                            try:
                                temperaturas[lugar_i] = (float(item[6]) + temperaturas[lugar_i])/2 
                            except:
                                temperaturas[lugar_i] = -99.99
                        else:
                            try:
                                temperaturas[lugar_i] = float(item[6])
                            except:
                                temperaturas[lugar_i] = -99.99
                    ## humedad
                    if(sensor_i=='humidity'):
                        try:
                            humedades[lugar_i] = float(valor_i)
                        except:
                            print "Error humedad"
                    ## checar gas
                    if(sensor_i =='gaslpg'):
                        gas[lugar_i] = valor_i
                        try:
                            if(float(valor_i) > 600):
                                globales['alarma_gas'] = True
                                lugar_gas = lugar_i
                                lectura = valor_i
                        except:
                            logging.error('Error float gas')



        ######### checar luces ########


        if(time.time()-check_lights_time > 15):
            #print "Check lights"
            try:
                check_lights_time = time.time()
                r_state = requests.get(ip_hue+'lights/', timeout=0.1)
                if(r_state.status_code == 200):
                    rs = r_state.json()
                    for key in rs:
                        estado_hue[rs[key]['name']] = rs[key]['state']['on']
                    #print estado_hue
                    logging.info('Estado luces: '+str(estado_hue))
            except:
                logging.error('Error getting light states')

        



        
        delta = time.time() - anterior
        #print delta
        for key in lugares:
            movimiento_st[key] = max(float(movimiento[key]),movimiento_st[key]*math.exp(-0.01*delta))  
        for key in movimiento_tv_st:
            movimiento_tv_st[key] = movimiento_tv_st[key]*math.exp(-0.01*delta)

        if(time.time() - dweepy_time > 10):
            dweepy_time = time.time()
            #print "registro dw 1"
            mov_send = {}
            for lugar in lugares:
                mov_send[lugar] = str(round(movimiento_st[lugar],2))
            #print mov_send
            logging.info('Estado movimiento:'+str(mov_send))
            try:
                #dweepy.dweet_for('well-groomed-move',mov_send)
                save_dweet('well-groomed-move',mov_send)

            except:
                print "error dweepy 1"
            
            gas_send = {}
            for key in gas:
                gas_send[key] = str(gas[key])
            hue_send = {}
            for key in estado_hue:
                hue_send[key] = str(int(estado_hue[key]))
            #try:
                #dweepy.dweet_for('cynical-powder',gas_send)
                #dweepy.dweet_for('fierce-cup',puertas)
                #dweepy.dweet_for('pleasant-fairies', hue_send)
            save_dweet('cynical-powder',gas_send)
            save_dweet('fierce-cup',puertas)
            save_dweet('pleasant-fairies',hue_send)
            #print 'pleasant-fairies'+str(hue_send)
            #except:
            #    print "error dweepy 2"
           
        anterior = time.time()
        if(time.time() - dweepy_time_2 > 23):
            #print "registro dw 2"
            dweepy_time_2 = time.time()
            temp_send = {}
            humid_send = {}
            for key in temperaturas:
                temp_send[key] = str(round(temperaturas[key], 2))
            for key in humedades:
                humid_send[key] = str(round(humedades[key], 2))
            try:
                #dweepy.dweet_for('zany-stomach',temp_send)
                save_dweet('verdant-credit', humid_send)
                save_dweet('zany-stomach',temp_send)
            except:
                print "Error dweepy zany 3"
            luz_send = {}
            for key in niveles_luz:
                luz_send[key] =str(niveles_luz[key])
            
            glob_send={}
            for key in globales:
                glob_send[key] = str(int(globales[key]))
            try:
                #dweepy.dweet_for('kindly-police',luz_send) 
                #dweepy.dweet_for('pretty-instrument',glob_send)
                save_dweet('kindly-police',luz_send) 
                save_dweet('pretty-instrument',glob_send)
                logging.info('Estado global:'+str(glob_send))
            except:
                print "error dweepy 4"


        ########## alarmas #########
        ## alertar por mensaje si alarma
        if(globales['alarma_trip'] and not(globales['alarma_enviada'])):
            encenderGrupo(luces['puerta'])
            encenderGrupo(luces['estudiof'])
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
                sonos.volume = 80
                texto_voz('Alarma de gas en ' + lugar_gas)
                #time.sleep(8)
                #decir('Alarma de gas en ' + lugar_gas)
                #sonos.volume = 40
            except:
                print "Error decir alarma de gas"


        ############ temperatura #########
        # activar aire si temperatura en tv es alta y hay alguien presente
        if(globales['activo'] and temperaturas['tv'] >= 24.5 and (not globales['ac_encendido']) and globales['auto_ac']):
            if(movimiento_st['tv'] > 0.4):
                xbee.tx(dest_addr_long='\x00\x13\xa2\x00\x40\xbf\x96\x2c',dest_addr='\x40\xb3', data=b'1')
                globales['ac_encendido'] = True
                actualizar_global('ac',int(globales['ac_encendido']), con2)

        if(temperaturas['tv'] < 22 and globales['ac_encendido'] and globales['auto_ac']):
            globales['ac_encendido'] = False
            xbee.tx(dest_addr_long='\x00\x13\xa2\x00\x40\xbf\x96\x2c',dest_addr='\x40\xb3', data=b'1')
            actualizar_global('ac',int(globales['ac_encendido']), con2)

            
        ##### chapa cerrar por seguridad #####
        if(chapa_por_cerrar and time.time()-tiempo_cerrar_chapa > 60*3):
            chapa(True, xbee=xbee)
            chapa_por_cerrar = False
            globales['chapa'] = True
      
           
        # procesar comandos pendientes
        if(time.time() - tiempo_comandos > 1.0):
            tiempo_comandos = time.time()
            concom = lite.connect('/Volumes/mmshared/bdatos/comandos.db')
            actuales = {}
            with concom:
                c = concom.cursor()
                c.execute('SELECT * FROM pendientes')
                actuales = c.fetchall()
                #print actuales
                c.executemany('DELETE FROM pendientes WHERE comando=? AND params=?',actuales)
            concom.close()   

                #print actuales
            if(len(actuales)>0):
                for comando in actuales:
                    #print comando
                    logging.info('Comando: '+str(comando))
                    if(comando[0]=='aire_acondicionado'):
                        print "Aire acondicionado"
                        xbee.tx(dest_addr_long='\x00\x13\xa2\x00\x40\xbf\x96\x2c',dest_addr='\x40\xb3', data=b'1')
                        globales['ac_encendido'] = not globales['ac_encendido']
                        actualizar_global('ac',int(globales['ac_encendido']), con2)
                    if(comando[0]=='apagar_luces'):
                        apagarTodas(luces)
                        #print "Apagando luces"
                    if(comando[0]=='abrir_garage'):
                        print "Abriendo garage"
                        texto_voz('Alguien abrió la puerta del garash')
                        try:
                            #r = requests.post('http://192.168.100.19:8090/garage')
                            r = requests.post('http://beaglebone.local:8090/garage')
                        except:
                            print "Error: Garage no disponible"
                        movimiento['entrada'] = True
                    if(comando[0]=='activar_alarma'):
                        if(comando[1]=='1'):
                            globales['alarma'] = True
                            globales['alarma_enviada'] = False
                            globales['alarma_trip'] = False
                            estado_sonos = tocar("alarma_activada.mp3")
                            chapa(True, xbee = xbee)
                            for key in luces:
                                apagarGrupo(luces[key])
                            globales['activo'] = False
                            actualizar_global('alarma', 1.0, con2)
                            actualizar_global('activo', 0.0, con2)
                        if(comando[1]=='0'):
                            globales['alarma'] = False
                            estado_sonos = tocar("alarma_desactivada.mp3")
                            chapa(False, xbee=xbee)
                            globales['alarma_trip']= False
                            globales['alarma_enviada'] = False
                            globales['activo'] = True
                            globales['alarma_gas'] = False
                            globales['alarma_gas_enviada'] = False
                            actualizar_global('alarma', 0.0, con2)
                            actualizar_global('activo', 1.0, con2)
                    ##### wit.ai
                    if(comando[0]=='decir'):
                        print "^^^^^^^^ decir"+comando[1]
                        texto = comando[1]
                        try:
                            texto_voz(texto)
                        except:
                            print "Error sonos ---------------------------"
                    if(comando[0]=='get_temperature'):
                        temps = temperaturas['sala']
                        texto_voz('La temperatura en la sala es de '+str(round(temps))+' grados')
                    #####
                    if(comando[0]=='dormir'):
                        dormir['cuarto'] = not dormir['cuarto']
                        if(dormir['cuarto']):
                            print "vol"
                            sonos.volume = 30
                            print "decir"

                            texto_voz('Listo para dormir')
                            print "apagar"
                            apagarGrupo(luces['cuarto'])
                            print "cerrar chapa"
                            chapa(True, xbee = xbee)
                        else:
                            sonos.volume=40
                            texto_voz('Hora de despertar')
                            sonos.volume =40
                    if(comando[0]=='luces_cocina' and comando[1]=='1'):
                        #print "Prender cocina"
                        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8\x62',command='D2',parameter='\x05')
                    if(comando[0]=='luces_cocina' and comando[1]=='0'):
                        #print "Apagar cocina"
                        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8\x62',command='D2',parameter='\x04')
                    if(comando[0]=='puerta_zumbador'):
                        print "Zumbando"
                        texto_voz('Alguien está llegando.')
                        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8\x62',command='D1',parameter='\x05')
                        tiempo_zumbador = time.time()
                        time.sleep(3)
                        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8\x62',command='D1',parameter='\x04')
                        movimiento['entrada'] = True

                    if(comando[0]=='chapa' and comando[1]=='1'):
                        print "Cerrar chapa"
                        chapa(True, xbee = xbee)
                    if(comando[0]=='chapa' and comando[1]=='0'):
                        print "Abrir chapa"
                        chapa(False, xbee = xbee)

                    if(comando[0]=='regar' and comando[1]=='1'):
                        print "Regar" #'0013a20040caadda'
                        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xca\xad\xda',command='D2',parameter='\x05')
                        globales['regadora'] = True
                        actualizar_global('regadora', int(globales['regadora']), con2)

                    if(comando[0]=='regar' and comando[1]=='0'):
                        print "no regar"
                        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xca\xad\xda',command='D2',parameter='\x04')
                        globales['regadora'] = False
                        actualizar_global('regadora', int(globales['regadora']), con2)


                    if(comando[0]=='auto_luces'):
                        print("Autoluz toggle")
                        #globales['activo'] = not globales['activo']
                        globales['auto_luces'] = not globales['auto_luces']
                        actualizar_global('auto_luces', int(globales['auto_luces']), con2)
                    if(comando[0]=='auto_ac'):
                        #globales['activo'] = not globales['activo']
                        globales['auto_ac'] = not globales['auto_ac']
                        actualizar_global('auto_ac', int(globales['auto_ac']), con2)
                    if(comando[0]=='alarmas_reset'):
                        globales['alarma_enviada'] = False
                        globales['alarma_gas_enviada'] = False
                        globales['alarma_gas'] = False
                        globales['alarma_trip'] = False

                        
                        #try:
                        #   with con2:
                        #        cur2 = con2.cursor()
                        #        command1 = "UPDATE status SET valor ="+int(activo)+" WHERE lugar='global' AND medicion= 'activo' AND no_sensor=1"
                        #        command2 = "UPDATE status SET timestamp ="+str(st)+" WHERE lugar='global' AND medicion= 'activo' AND no_sensor=1"
                        #        cur2.execute(command1)
                        #        cur2.execute(command2)
                        #except:
                        #    print "Error activo escribir"
               
        
        # nivel de luz afuera
        now_1 = datetime.datetime.now().time()
        if(time_in_range(datetime.time(18, 0, 0),datetime.time(8, 0, 0), now_1)):
            niveles_luz['entrada'] = 600
        else:
            niveles_luz['entrada'] = 900   
        # encender luces donde haya movimiento, si están apagadas?
        for key in movimiento:
            if(movimiento[key]):
                tiempo_movimiento[key] = time.time()
                if(niveles_luz[key] < nivel_encendido[key]):
                    if(globales['activo'] and (not dormir[key])):       
                        if(time.time() - tiempo_encendido[key] > 10):
                            #print "Encender luces"
                            if(key=='cocina'):
                                print("Encender cocina, movimiento.")
                                xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8\x62',command='D2',parameter='\x05')
                            else:

                                encenderGrupo(luces[key])
                            tiempo_encendido[key] = time.time()
                            estado_luces[key] = True
                                
                            

        ## actividades programadas
        if((not globales['regadora']) and dt.hour==21 and dt.minute < 2):
            globales['regadora']=True
            xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xca\xad\xda',command='D2',parameter='\x05')
            actualizar_global('regadora', int(globales['regadora']), con2)
        if(globales['regadora'] and dt.hour==1):
            xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xca\xad\xda',command='D2',parameter='\x04')
            globales['regadora'] = False
            actualizar_global('regadora', int(globales['regadora']), con2)

        if(dormir['cuarto'] and dt.hour==8):
            print 'Despertador'
            sonos.stop()
            sonos.volume = 40
            
            #time.sleep
            parte_dia='mañana'
            if(dt.hour>=12):
                parte_dia = 'tarde'
                if(dt.hour>=20):
                    parte_dia = 'noche'
            sonos.volume = 60
            if(dt.minute>0):
                texto_voz('Hora de despertar! Son las '+str(dt.hour)+' con '+str(dt.minute))
            else:
                texto_voz('Hora de despertar! Son las '+str(dt.hour)+' en punto')

            #decir('')
            dormir['cuarto'] = False


        ## pings
        #if(time.time() - felipe_phone_time > 10):
        #   pass
            #felipe_iphone = subprocess.call('ping -q -c1 -W 1 '+ '192.168.100.6' + ' > /dev/null', shell=True)
            #tere_iphone = subprocess.call('ping -q -c1 -W 1 '+ '192.168.100.7' + ' > /dev/null', shell=True)
            #felipe_phone_time = time.time()

            #if(felipe_iphone==0):
            #    globales['felipe'] = True
            #else:
            #    globales['felipe'] = False
            #if(tere_iphone==0):
            #    globales['tere'] = True
            #else:
            #    globales['tere'] = False


        ### registrar sensores
        try:
            if(time.time()-mom_registrar[lugar] > delay_registro[lugar]):
                mom_registrar[lugar] = time.time()
                #print ocurrencia
                if 'ocurrencia' in locals():
                    for item in ocurrencia:
                        #pass
                        #print(item)
                        #print item
                        update_ultimas(item, con2, str(st))
            if 'ocurrencia' in locals():
                for item in ocurrencia:
                    if item[3] == 'pressure':
                       # print "Pressure"
                        if(time.time()-tiempo_pressure > delay_pressure):
                            update_ultimas(item, con2, str(st))
                            tiempo_pressure=time.time()

        except:
            print("error registro ultimas")



        nuevo_tiempo = time.time() - tstamp
        tiempos.append(nuevo_tiempo)
        ant = tiempos.popleft()
        #time_loop = time.time()
        
        if((time.time()-log_time) > 20):
            print time.time()-log_time
            log_time = time.time()
            actualizar_global('heartbeat', round(sum(tiempos)/len(tiempos),2), con2)
            print '\033[91m'+'Media: '+str(round(sum(tiempos)/len(tiempos),2))+'  Max: '+str(round(max(tiempos),2))+'\033[0m'
        
            #print "Luz, ", niveles_luz
            #print "Temperatura, ", temperaturas
            #print "Humedad", humedades
            #decir('La temperatura es '+str(round(temperaturas['sala']))+' grados')
            print "Movimiento, ", movimiento
            #print "Mov st ", movimiento_st
            print "Globales ", globales
            print " "
            print " "
            if(int(globales['mA']) > 20000):
                texto_voz('Están usando más de '+ str(math.floor(float(globales['mA'])/1000)) + ' amperios.')
            latencia = round(sum(tiempos)/len(tiempos),2)
            if(latencia > 2):
                texto_voz('Latencia de '+str(round(sum(tiempos)/len(tiempos),2))+' segundos' )
        #print estado_sonos
        #print time.time() - estado_sonos['tiempo_inicio'], estado_sonos['alertDuration']
        if((time.time() - estado_sonos['tiempo_inicio']) > estado_sonos['alertDuration']):
            try:
                print "Continuar sonos"
                estado_sonos['alertDuration'] = 10000000
                #continuar_sonos(estado_sonos)

            except:
                'Error continuar sonos ****'




            
##############################################################################
def save_dweet(thing, obj):
    #print "Saving dweets"
    pdata = cPickle.dumps((thing, obj), cPickle.HIGHEST_PROTOCOL)
    redis_q.rpush('queue', pdata)

    #with con_dweet:
    #    curr_d = con_dweet.cursor()
    #    pdata = cPickle.dumps(obj, cPickle.HIGHEST_PROTOCOL)
    #    st_command="insert into dweets (thing, dweet) values ("+thing+",:data)"
    #    curr_d.execute("insert into dweets (thing, dweet) values (?,?)", [thing,lite.Binary(pdata)])
   



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
            inicial = time.time()
            r = requests.put(ip_hue + 'lights/'+str(luz)+'/state', data=payoff, timeout=0.5)
            final = time.time()
            logging.info('Luces :'+'apagar '+str(luz)+'|' +str(final-inicial))
        except:
            print "Luces no disponibles para apagar" + str(grupo)
def encenderGrupo(grupo):
   for luz in grupo:
        try:
            inicial = time.time()
            state_hue = requests.get(ip_hue+'lights/'+str(luz), timeout=0.2)
            if(not json.loads(state_hue.content)['state']['on']):
                r = requests.put(ip_hue + 'lights/'+str(luz)+'/state', data=payon, timeout=0.5)
                logging.info('Luces :'+'encender '+str(luz)+'|'+str(final-inicio))
            final = time.time()
            
        except:
            print "Luces no disponibles para encender" + str(grupo)

def apagarTodas(luces):
    for zona in luces:
        apagarGrupo(luces[zona])
    #xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8\x62',command='D2',parameter='\x04')

def chapa(cerrar, xbee):
    if(cerrar):
        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='P2',parameter='\x05')
        time.sleep(0.2)
        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='P2',parameter='\x04')
        globales['chapa'] = True
        actualizar_global('chapa', 1.0, con2)

    else:
        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='D0',parameter='\x05')
        time.sleep(0.2)
        xbee.remote_at(dest_addr_long= '\x00\x13\xa2\x00@\xbe\xf8M',command='D0',parameter='\x04')
        globales['chapa'] = False
        actualizar_global('chapa', 0.0, con2)

def actualizar_global(item,valor, con2):
    
    tstamp = time.time()
    st = datetime.datetime.fromtimestamp(tstamp, tz=tzone).strftime('%Y-%m-%d %H:%M:%S')

    try:
        with con2:
            cur2 = con2.cursor()
            command1 = "UPDATE status SET valor ="+str(valor)+", timestamp='"+str(st) +"' WHERE lugar='global' AND medicion= '"+item+"' AND no_sensor=1"
            #print command1
            cur2.execute(command1)
    except:
        print "Error sqlite globales ultimas"


def update_ultimas(item, con2, ts):
    try:
        with con2:
            cur2 = con2.cursor()
            valbase = item[6]
            if(isinstance(item[6], bool)):
                try:
                    valbase = float(item[6])
                except:
                    valbase = -20.0
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

def continuar_sonos(estado_sonos):
    track = estado_sonos['track']
    mediaInfo = estado_sonos['mediaInfo']
    playlistPos = int(track['playlist_position'])-1
    trackPos = track['position']
    trackURI = track['uri']
    mediaURI = mediaInfo['CurrentURI']
    mediaMeta = mediaInfo['CurrentURIMetaData']
    sonos.volume = estado_sonos['volumen']
    if(estado_sonos['state']=='PLAYING'):
        if(len(sonos.get_queue()) > 0 and playlistPos > 0):
            print 'Resume queue from %d: %s - %s' % (playlistPos, track['artist'], track['title'])
            sonos.play_from_queue(playlistPos)
            sonos.seek(trackPos)
        else:
            print 'Resuming %s' % mediaURI
            sonos.play_uri(mediaURI, mediaMeta)

def tocar(archivo):
    try:
        track = sonos.get_current_track_info()
        #playlistPos = int(track['playlist_position'])-1
        #trackPos = track['position']
        #trackURI = track['uri']

    # This information allows us to resume services like Pandora
        mediaInfo = sonos.avTransport.GetMediaInfo([('InstanceID', 0)])
        #mediaURI = mediaInfo['CurrentURI']
        #mediaMeta = mediaInfo['CurrentURIMetaData']
        transport_state = sonos.get_current_transport_info()['current_transport_state']
        volumen = sonos.volume
        sonos.play_uri('x-file-cifs://homeserver/sonidos/'+archivo)
        duration_txt = sonos.get_current_track_info()['duration']
        alertDuration = int(duration_txt.split(':')[2])
        #sleepTime=2
        #time.sleep(sleepTime)
        #if len(zp.get_queue()) > 0 and playlistPos > 0:
        #    print 'Resume queue from %d: %s - %s' % (playlistPos, track['artist'], track['title'])
        #    sonos.play_from_queue(playlistPos)
        #    sonos.seek(trackPos)
        #else:
        #    print 'Resuming %s' % mediaURI
        #    sonos.play_uri(mediaURI, mediaMeta)
        tiempo = time.time()
        estado_salida = {'track':track, 'mediaInfo':mediaInfo, 
                        'alertDuration':alertDuration, 'tiempo_inicio':tiempo,
                        'state':transport_state, 'volumen':volumen}
        #print estado_salida
        return estado_salida

    except ValueError:
        print "Error sonos"

def texto_voz(texto):
    estado_s = {}
    try:
        os.system("say -v Paulina '"+texto+"' -o "+"/Volumes/mmshared/sonidos/voz.mp4")
        estado_s = tocar("voz.mp4")
        #sonos.play_uri('x-file-cifs:%s' % '//homeserver/sonidos/voz.mp4')
    except:
        print "Error say!"
    return estado_s


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
    

    try:
        ok, file_name =  text2mp3(texto, PATH, LANGUAGE, ALERT)

        if ok:
            #zp = SoCo(ip_sonos)
            print('x-file-cifs:%s' % '//homeserver/sonidos/speech.mp3')
            sonos.play_uri('x-file-cifs:%s' % '//homeserver/sonidos/speech.mp3')
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
    except:
        print "Error text2speech"


def decir2(texto):
    track = sonos.get_current_track_info()
    playlistPos = int(track['playlist_position'])-1
    trackPos = track['position']
    trackURI = track['uri']

    # This information allows us to resume services like Pandora
    mediaInfo = sonos.avTransport.GetMediaInfo([('InstanceID', 0)])
    mediaURI = mediaInfo['CurrentURI']
    mediaMeta = mediaInfo['CurrentURIMetaData']

    ok, file_name =  text2mp3(texto, PATH, LANGUAGE, False)
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

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

# if run as top-level script
if __name__ == "__main__":
    try:
        monitorCasa()
    except KeyboardInterrupt:
        #GPIO.output("P8_10", GPIO.LOW)    
        conlocal.close()
        #conrds.close()
        pass
