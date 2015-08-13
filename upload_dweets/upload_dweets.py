import requests
import json
import dweepy
import cPickle
import sqlite3 as lite
import time
import redis
con_dweet= lite.connect('/Volumes/mmshared/bdatos/to_dweet.db')
redis_q = redis.Redis()

def uploadDweet():
    time_d = time.time()

    while(True):
        if(time.time()-time_d > 5):
            print "Sending data, " + str(time.time())
            time_d = time.time()
            while (redis_q.llen('queue') > 0):
                print "Queue len: %s" % redis_q.llen('queue')
                message = redis_q.blpop('queue')
                message_d = cPickle.loads(message[1])
                thing = message_d[0]
                data = message_d[1]
                try:
                    #pass
                    dweepy.dweet_for(thing, data)
                except:
                    print "Error dweepy"
            print "cleared queue"
            #with con_dweet:
            #    c = con_dweet.cursor()
            #    c.execute('SELECT * FROM dweets')
            #    actuales = c.fetchall()
                #file = open('/Volumes/mmshared/bdatos/log/dweets_'+time.strftime("%d-%m-%Y")+'.dat', 'a+')
            #    for dweets in actuales:
            #        thing = dweets[0]
            #        data = cPickle.loads(str(dweets[1]))
            #        try:
                        #file.write(time.strftime("%d-%m-%Y %H:%M:%S")+','+thing+','+json.dumps(data)+'\n')
            #            dweepy.dweet_for(thing, data)
            #        except:
            #            print "Error subiendo dweets"
            #    c.execute('DELETE FROM dweets')
                #file.close()


if __name__ == "__main__":
    try:
        uploadDweet()
    except KeyboardInterrupt:
        #GPIO.output("P8_10", GPIO.LOW)    
        #con_dweet.close()
        #conrds.close()
        pass
