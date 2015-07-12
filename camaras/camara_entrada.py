#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
import datetime


def snapshot():
    try:
        r = requests.get('http://raspicam.local:8080')

        rs = requests.get('http://raspicam.local:8080/img/sshot.jpg')
        ts = time.time()
        ts_t = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H_%M_%S')
        path ="/Volumes/mmshared/imagenes/imagen"+str(ts_t)+".jpg"
        path_actual = "/Users/felipe/servidor_casa/cherrypy/img/imagen_garage.jpg"
        print path
        if rs.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in rs:
                    f.write(chunk)
            with open(path_actual, 'wb') as f_act:
                for chunk in rs:
                    f_act.write(chunk)
    except:
        print "Request/write error"
    return 1

if __name__ == "__main__":
    try:
        while True:

            snapshot()
            time.sleep(5)
    except KeyboardInterrupt:
        pass