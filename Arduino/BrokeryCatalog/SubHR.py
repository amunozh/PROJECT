# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 01:56:26 2019

@author: Miguel
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 10:47:44 2019

@author: Shuyang
"""


import time
import paho.mqtt.client as Paho
import json



class Meter(object):


    def __init__(self,name,sub_topic,pub_topic,broker):
        self.client = Paho.Client(name)
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.broker = broker
        self.client.on_message = self.on_message
        self.timer = Timer()


    def start(self):
        self.client.connect(self.broker)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()


    def publish(self,msg):
        self.client.publish(self.pub_topic,msg)

    def subscribe(self):
        self.client.subscribe(self.sub_topic)


    def on_message(self,client,userdata,message):
        content = json.loads(message.payload)
#        print(content)
        print("We got a message!")
        print('Topic: %s Message: %s' % (message.topic,content))
        return




class Timer(object):


    def __init__(self):
        self.timer = False

    def start(self):
        self.timer = time.time()

    def stop(self):
        time_c = time.time()-self.timer
        self.timer = False
        return time_c

    def get_time(self):
        if self.timer == False:
            return False
        else:
            return time.time()-self.timer




if __name__ == '__main__':


    c = Meter('s','Miguel1096/test/HR','Miguel1096/test/HR',"mqtt.eclipse.org")



    c.start()
    counter = 0
    c.subscribe()
    
    
#    while counter < 15:
#        if counter == 2:
#            c.publish(json.dumps({'input':'on'}))
#        elif counter == 4:
#            c.publish(json.dumps({'input':'check'}))
#        if counter == 13:
#            c.publish(json.dumps({'input':'off'}))
#        counter += 1
#        time.sleep(1)
    time.sleep(30)
    c.stop()
