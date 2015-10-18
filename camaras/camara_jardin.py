#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
import datetime
import sys


def snapshot():
    try:
        r = requests.get('http://raspi-jardin.local:8080/camara_alta')

        rs = requests.get('http://raspi-jardin.local:8080/img/sshot.jpg', stream = True)
        ts = time.time()
    except:
        "Request error"
    try:
        ts_t = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H_%M_%S')
        path ="/Volumes/mmshared/imagenes/imagen_jardin_"+str(ts_t)+".jpg"
        path_actual = "/Users/felipe/servidor_casa/cherrypy/img/imagen_jardin.jpg"
        print path
        if rs.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in rs:
                    f.write(chunk)
            #with open(path_actual, 'wb') as f_act:
            #    for chunk in rs:
            #        f_act.write(chunk)
    except:
        print sys.exc_info()[0]
        print "Write error"
    return 1

if __name__ == "__main__":
    try:
        while True:

            snapshot()
            time.sleep(60*20)
    except KeyboardInterrupt:
        pass