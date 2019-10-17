# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:41:38 2019

@author: Miguel
"""

import time
import paho.mqtt.client as Paho
import json
import requests



class Meter(object):


    def __init__(self,name,sub_topic,pub_topic,broker,IPs):
        self.client = Paho.Client(name)
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.broker = broker
        self.client.on_message = self.on_message
        self.topic_names=[]
        self.IPs = IPs
        self.timer = Timer(IPs)


    def start(self):
        self.client.connect(self.broker)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()


    def publish(self,Topic,msg):
        if (Topic!="0"):
            self.client.publish(Topic,msg,qos=0)


    def subscribe(self):
        self.client.subscribe(self.sub_topic)


    def on_message(self,client,userdata,message):
        content = json.loads(message.payload)
        print("We got a message!")
        print('Topic: %s Message: %s' % (message.topic,content))
        X=float(content["e"][0]["v"])
        (Topic,Flag)=self.timer.check(message.topic,X)
        if Flag!="0":
            self.publish(Topic,Flag)
            print("Alarm: %s" % (Topic))
        return




class Timer(object):

    def __init__(self, IPs):
        self.timer = False
        self.IPs = IPs

    def check(self,Topic,HR):
        meg="0";
        if HR>=130:
            meg=json.dumps({'Alarm':'High HR','BPM':HR})
        elif HR<=70:
            meg=json.dumps({'Alarm':'Low HR','BPM':HR})
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

class IPS(object):
    def __init__(self, IPAdd,PAdd,IPCat,PCat,IPBroker,PBroker,):
        self.IPAdd=IPAdd
        self.IPCat=IPCat
        self.IPBroker=IPBroker
        self.PAdd=PAdd
        self.PCat=PCat
        self.PBroker=PBroker


if __name__ == '__main__':
    
    IPAddr="192.168.1.122"
    PortAddr="8181"
    #Contact to Address Manager to get the Catalog IP and Port
    response = requests.get("http://"+IPAddr+":"+PortAddr + "/address_manager/get")
    r=response.content.decode('utf-8')
    jr=json.loads(r)
    print(jr)
    IPCat=jr['ip']
    PortCat=str(jr['port'])

    # Contact to Catalog to Register as Service
    aux=json.dumps({'ID':'AlarmBPM','end_point':['/Service/Alarms',None],'resources':['BPM_Alarm']})
    response = requests.post("http://" + IPCat + ":"+ PortCat + "/catalog/add_service?json_msg="+aux)
    r=response.content.decode('utf-8')
    print(r)

    # Contact to Catalog to get the Broker IP and Port
    response = requests.get("http://" + IPCat + ":"+PortCat + "/catalog/broker")
    r = response.content.decode('utf-8')
    jr = json.loads(r)
    print(jr)
    IPBroker = jr['ip']
    PortBroker = jr['port']

    #Save all IPs and Ports in a Variable
    Dir = IPS(IPAddr, PortAddr, IPCat, PortCat, IPBroker, PortBroker)

    #Create the MQTT Client to Receive Data and Reply in case of Anormal Values of BPM
    #              Name , Sub Topic , Pub Topic , Broker IP , IPs
    c = Meter('AlarmBPM','/+/BPM','Services/Alarm',Dir.IPBroker,Dir)

    c.start()

    c.subscribe()

    time.sleep(100)
    c.stop()