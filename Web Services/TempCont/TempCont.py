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

    def __init__(self, name, sub_topic, pub_topic, broker,IPs):
        self.client = Paho.Client(name)
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.broker = broker
        self.client.on_message = self.on_message
        self.topic_names = []
        self.IPs=IPs
        self.timer = Timer(IPs)

    def start(self):
        self.client.connect(self.broker)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, Topic, msg):
        if (Topic != "0"):
            self.client.publish(self.pub_topic, msg, qos=0)
        else:
            self.client.publish(Topic, msg, qos=0)

    def subscribe(self):
        self.client.subscribe(self.sub_topic)

    def on_message(self, client, userdata, message):
        content = json.loads(message.payload)
        #        print(content)
        print("We got a message!")
        print('Topic: %s Message: %s' % (message.topic, content))
        #        self.topic_names.append(message.topic)
        Topic = "0"
        ID=content["bn"]
        X = float(content["e"][0]["v"])
        (Url,Flag) = self.timer.check(ID,X)
        if Flag != "0":
            response = requests.get("http://" + self.IPs.IPCat + ":" + self.IPs.PCat + "/catalog/search/" + Act)

        return


class Timer(object):

    def __init__(self,IPs):
        self.timer = False
        self.IPs=IPs

    def check(self, Y, HR):
        meg = "0";
        aux=int(HR)
        if HR <= 18 or HR>=28:
            Act=Y[0]+Y[1]+"A"+Y[3]+Y[4]
            response = requests.get("http://" + self.IPs.IPCat + ":"+self.IPs.PCat + "/catalog/search/"+Act)
            r = response.content.decode('utf-8')
            jr = json.loads(r)
            Url=jr["end_point"][1]
            meg = "25"

        # elif HR <= 28:
        #     Act = Y[0] + Y[1] + "A" + Y[3] + Y[4]
        #     response = requests.get("http://" + self.IPs.IPCat + ":" + self.IPs.PCat + "/catalog/search/" + Act)
        #     r = response.content.decode('utf-8')
        #     jr = json.loads(r)
        #     Url = jr["end_point"][1]
        #     meg = "25"
        #     meg = json.dumps({'Alarm': 'Low HR'})
        else:
            Url = "0"

        return (Url, meg)

    def stop(self):
        time_c = time.time() - self.timer
        self.timer = False
        return time_c

    def get_time(self):
        if self.timer == False:
            return False
        else:
            return time.time() - self.timer

class IPS(object):
    def __init__(self, IPAdd,PAdd,IPCat,PCat,IPBroker,PBroker,):
        self.IPAdd=IPAdd
        self.IPCat=IPCat
        self.IPBroker=IPBroker
        self.PAdd=PAdd
        self.PCat=PCat
        self.PBroker=PBroker


if __name__ == '__main__':
    IPAddr = "192.168.1.193"
    PortAddr = "8181"
    response = requests.get("http://" + IPAddr + ":8181" + "/address_manager/get")
    r = response.content.decode('utf-8')
    jr = json.loads(r)
    print(jr)

    IPCat = jr['ip']
    PortCat = jr['port']
    print(IPCat)
    print(PortCat)
    response = requests.post(
        "http://" + IPCat + ":" + PortCat + "/catalog/add_service?json_msg={'ID':'Temperature_Control','end_point':['/Service/Temperature_Control'],'resources':['temp']}")
    r = response.content.decode('utf-8')
    print(r)

    response = requests.get("http://" + IPCat + ":8282" + "/catalog/broker")
    r = response.content.decode('utf-8')
    jr = json.loads(r)
    print(jr)
    IPBroker= jr['ip']
    PortBroker = jr['port']
    print(IPBroker)
    print(PortBroker)
    Dir=IPS(IPAddr,PortAddr,IPCat,PortCat,IPBroker,PortBroker)

    c = Meter('s', '/+/temp', 'Services/Temperature_Control', Dir.IPBroker,IPS)
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