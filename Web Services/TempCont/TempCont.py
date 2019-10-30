# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:41:38 2019

@author: Miguel
"""

import time
import paho.mqtt.client as Paho
import json
import requests
from random import randint

#Class in charge of Handle the MQTT Messages
class Meter(object):

    def __init__(self, name, sub_topic, pub_topic, broker,IPs):
        self.client = Paho.Client(name)
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.broker = broker
        self.client.on_message = self.on_message
        self.topic_names = []
        self.IPs=IPs
        self.controller = controller(IPs)

    def start(self):
        self.client.connect(self.broker)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, msg):
        self.client.publish(self.pub_topic, msg, qos=0)


    def subscribe(self):
        self.client.subscribe(self.sub_topic)

    def on_message(self, client, userdata, message):

        content = json.loads(message.payload)
        print("We got a message!")
        print('Topic: %s Message: %s' % (message.topic, content))
        ID=content["bn"]
        X = float(content["e"][0]["v"])

        Url = self.controller.ledController(ID,X)
        response = requests.get(Url)
        r = response.content.decode('utf-8')
        print(r)
        
        return

#Class in charge of Store the IP Addresses
class IPS(object):
    def __init__(self, IPAdd,PAdd,IPCat,PCat,IPBroker,PBroker,):
        self.IPAdd=IPAdd
        self.IPCat=IPCat
        self.IPBroker=IPBroker
        self.PAdd=PAdd
        self.PCat=PCat
        self.PBroker=PBroker

#Class in charge of Monitor the Temperature received on the message
class controller(object):
    
    def __init__(self, IPs):
        self.IPs=IPs

    def ledController(self, Y, temperature):
        
        self.temp=int(temperature)
        Act=Y[0]+Y[1]+"A"+Y[3]+Y[4]
        js=json.dumps({'ID':Act})
        response = requests.get("http://" + self.IPs.IPCat + ":"+self.IPs.PCat + "/catalog/search_device?json_msg=" + js)
        r = response.content.decode('utf-8')
        jr = json.loads(r)
        Url=jr["end_point"][1]
        print(Url)
        if (self.temp < 0):
            value = randint(80, 100)
            url="/actuator/warm?intensity="+str(value)
        elif (0 <= self.temp and self.temp < 10):
            value = randint(50, 80)
            url="/actuator/warm?intensity="+str(value)
        elif (10 <= self.temp and self.temp < 18):
            value = randint(30, 50)
            url="/actuator/warm?intensity="+str(value)
        elif (23 <= self.temp and self.temp < 28):
            value = randint(30, 50)
            url="/actuator/cold?intensity="+str(value)
        elif (28 <= self.temp and self.temp < 35):
            value = randint(50, 80)
            url="/actuator/cold?intensity="+str(value)
        elif (self.temp >= 35):
            value = randint(80, 100)
            url="/actuator/cold?intensity="+str(value)
        else:
            url="/actuator/cold?intensity=20"


        return(Url+url)


if __name__ == '__main__':
    IPAddr = "192.168.1.122"
    PortAddr = "8585"
    # Contact to Address Manager to get the Catalog IP and Port
    response = requests.get("http://" + IPAddr + ":" + PortAddr + "/address_manager/get")
    r = response.content.decode('utf-8')
    jr = json.loads(r)
    print(jr)
    IPCat = jr['ip']
    PortCat = str(jr['port'])

    # Contact to Catalog to Register as Service
    aux = json.dumps({'ID': 'TempControl', 'end_point': ['/Service/TempControl', None], 'resources': ['temp']})
    response = requests.post("http://" + IPCat + ":" + PortCat + "/catalog/add_service?json_msg="+aux)
    r = response.content.decode('utf-8')
    print(r)

    # Contact to Catalog to Get Broker Address
    response = requests.get("http://" + IPCat + ":"+PortCat + "/catalog/broker")
    r = response.content.decode('utf-8')
    jr = json.loads(r)
    print(jr)
    IPBroker= jr['ip']
    PortBroker = jr['port']

    Dir=IPS(IPAddr,PortAddr,IPCat,PortCat,IPBroker,PortBroker)

    c = Meter('TempControl', '/+/humi_temp', 'Services/Temperature_Control', Dir.IPBroker,IPS)
    #
    #
    #
    c.start()
    c.subscribe()
    while (True):
        time.sleep(100)
        #c.stop()