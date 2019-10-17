# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:41:38 2019

@author: Miguel
"""

import time
import paho.mqtt.client as Paho
import json
import requests
from requests.exceptions import Timeout


class Meter(object):


    def __init__(self,name,sub_topic,pub_topic,broker):
        self.client = Paho.Client(name)
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.broker = broker
        self.client.on_message = self.on_message
        self.timer = Timer()
        self.topic_names=[]


    def start(self):
        self.client.connect(self.broker)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()


    def publish(self,Topic,msg):
        if (Topic!="0"):
            self.client.publish(self.pub_topic,msg,qos=0)
        else:
            self.client.publish(Topic,msg,qos=0)

    def subscribe(self):
        self.client.subscribe(self.sub_topic)


    def on_message(self,client,userdata,message):
        content = json.loads(message.payload)
#        print(content)
        print("We got a message!")
        print('Topic: %s Message: %s' % (message.topic,content))
#        self.topic_names.append(message.topic)
        Topic="0"
        X=float(float(content["e"][0]["v"]))
        (Topic,Flag)=self.timer.check(message.topic,X)
        if Flag!="0":
            self.publish(Topic,Flag)
            print("Alarm: %s" % (Topic))
        return




class Timer(object):


    def __init__(self):
        self.timer = False

    def check(self,Topic,HR):
        meg="0";
        if HR>=130:
            meg=json.dumps({'Alarm':'High HR'})
            
        elif HR<=70:
            meg=json.dumps({'Alarm':'Low HR'})
            
        else:
            Topic="0"

        return (Topic,meg)
        

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
    
    IPAddr="192.168.1.122"
    
    response = requests.get("http://"+IPAddr+":8181" + "/address_manager/get")
    r=response.content.decode('utf-8')
    jr=json.loads(r)
    print(jr)
    
    IPCat=jr['ip']
    PortCat=str(jr['port'])
    aux=json.dumps({'ID':'AlarmBPM','end_point':['/Service/Alarms',None],'resources':['BPM_Alarm']})

    response = requests.post("http://" + IPCat + ":"+ PortCat + "/catalog/add_service?json_msg="+aux)
    r=response.content.decode('utf-8')
    print(r)

    c = Meter('AlarmBPM','/+/BPM','Services/Alarm',"192.168.1.6")
#
#
#
    c.start()
    counter = 0
    c.subscribe()
#    
#    
##    while counter < 15:
##        if counter == 2:
##            c.publish(json.dumps({'input':'on'}))
##        elif counter == 4:
##            c.publish(json.dumps({'input':'check'}))
##        if counter == 13:
##            c.publish(json.dumps({'input':'off'}))
##        counter += 1
##        time.sleep(1)
    time.sleep(100)
    c.stop()