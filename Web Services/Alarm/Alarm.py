# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:41:38 2019

@author: Miguel
"""

import time
import paho.mqtt.client as Paho
import json
import requests


#Class in charge of Handle the MQTT Messages
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
        a=message.topic
        top=a[1:6]
        (Top,Flag)=self.timer.check(top,X)
        if Flag!="0":
            Topic=self.pub_topic+Top
            self.publish(Topic,Flag)
            print("Alarm: %s" % (Topic))
        return
#Class in charge of Monitor the HR received on the message
class Timer(object):

    def __init__(self, IPs):
        self.timer = False
        self.IPs = IPs

    def check(self,Topic,HR):
        meg="0";
        if HR>=150:
            meg=json.dumps({'Topic':Topic,'Alarm':'High HR','BPM':HR})
        elif HR<=50:
            meg=json.dumps({'Topic':Topic,'Alarm':'Low HR','BPM':HR})
        else:
            Topic="0"
        return (Topic,meg)

#Class in charge of Store the IP Addresses
class IPS(object):
    def __init__(self, IPAdd,PAdd,IPCat,PCat,IPBroker,PBroker,):
        self.IPAdd=IPAdd
        self.IPCat=IPCat
        self.IPBroker=IPBroker
        self.PAdd=PAdd
        self.PCat=PCat
        self.PBroker=PBroker


if __name__ == '__main__':
    
    IPAddr="192.168.1.123"
    PortAddr="8585"
    #Contact to Address Manager to get the Catalog IP and Port
    response = requests.get("http://"+IPAddr+":"+PortAddr + "/address_manager/get")
    r=response.content.decode('utf-8')
    jr=json.loads(r)
    print(jr)
    IPCat=jr['ip']
    PortCat=str(jr['port'])

    # Contact to Catalog to Register as Service
    aux=json.dumps({'ID':'AlarmBPM01','end_point':['/Service/Alarms',None],'resources':['BPM_Alarm']})
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
    c = Meter('AlarmBPM','/+/BPM','/Alerts/',Dir.IPBroker,Dir)

    c.start()

    c.subscribe()
    while (True):
        time.sleep(100)
    #c.stop()