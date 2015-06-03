import requests
import json
import dweepy
import cPickle
import sqlite3 as lite
import time

con_dweet= lite.connect('/Volumes/mmshared/bdatos/to_dweet.db')


def uploadDweet():
    time_d = time.time()

    while(True):
        if(time.time()-time_d > 20):
            print "Sending data"
            time_d = time.time()
            with con_dweet:
                c = con_dweet.cursor()
                c.execute('SELECT * FROM dweets')
                actuales = c.fetchall()
                file = open('/Volumes/mmshared/bdatos/log/dweets_'+time.strftime("%d-%m-%Y")+'.dat', 'a+')
                for dweets in actuales:
                    thing = dweets[0]
                    data = cPickle.loads(str(dweets[1]))
                    try:
                        file.write(time.strftime("%d-%m-%Y %H:%M:%S")+','+thing+','+json.dumps(data)+'\n')
                        dweepy.dweet_for(thing, data)
                    except:
                        print "Error subiendo dweets"
                c.execute('DELETE FROM dweets')
                file.close()


if __name__ == "__main__":
    try:
        uploadDweet()
    except KeyboardInterrupt:
        #GPIO.output("P8_10", GPIO.LOW)    
        con_dweet.close()
        #conrds.close()
        pass
