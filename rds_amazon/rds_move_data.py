#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb 
import sqlite3 as lite
import time

def moverDatos():
    print "Comenzar monitoreo de datos"
    #conrds = MySQLdb.connect(host="fgdbinstances.cqgwstytvlnn.us-east-1.rds.amazonaws.com", port =3306,user="felipe",passwd="valqui2312",db="dbmonitor")
    conrds = MySQLdb.connect(host='localhost', user = 'felipe', db='casa')
    print conrds
    print "Amazon RDS conectada."
    conlocal = lite.connect('/Volumes/mmshared/bdatos/temp_monitor.db')
    print "Base local conectada."
    print conlocal

    while True:
        print "Ciclo de lectura"
        time.sleep(30)
        conlocal = lite.connect('/Volumes/mmshared/bdatos/temp_monitor.db')

        with conlocal:
            print "Seleccionando datos"
            c = conlocal.cursor()
            c.execute('SELECT * FROM monitorlocal')
            actuales = c.fetchall()
            
            print "Escribiendo a rds"
            for item in actuales:
                with conrds:
                    curds = conrds.cursor()
                    comand_base = 'insert into mediciones (tiempo_reg, xbee, lugar, tipo, unidad, num_sensor, valor) VALUES '
                    comand_2 ="('"+item[0]+"','"+item[1]+"','"+item[2]+"','"+item[3]+"','"+item[4]+"','"+str(int(item[5]))+"',"+str(float(item[6]))+")"
                    commandx = comand_base+comand_2
                    #print "."
       #print commandx
                    curds.execute(commandx)
            

            print "Datos en rds..."
        
            with conlocal:
                c = conlocal.cursor()
                c.execute('DELETE FROM monitorlocal')
        conlocal.close()
# if run as top-level script
if __name__ == "__main__":
    try:
        moverDatos()
    except KeyboardInterrupt:
        #GPIO.output("P8_10", GPIO.LOW)    
        con.close()
        conrds.close()
        pass