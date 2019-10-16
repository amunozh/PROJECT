#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 13:36:20 2018

@author: pi
"""

import paho.mqtt.client as paho
import requests
import Adafruit_DHT as ada
import json
import time


class DHT11_Clients :

    def __init__(self,ID,broker,pub_topic,sub_topic,port=None):
        self.Id = ID
        self.broker = broker
        self.port = port
        self.pub_topic = pub_topic
        self.sub_topic = sub_topic
        self.client = paho.Client(ID)
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

    def start_loop(self):
        if self.port == None:
            self.client.connect(self.broker)
        else:
            self.client.connect(self.broker,self.port)
        self.client.loop_start()

    def stop_loop(self):
        self.client.disconnect()
        self.client.loop_stop()


    def publish(self,payload):
        self.client.publish(self.pub_topic,payload)


    def on_connect(self,client,userdata,flags,rc):
        print self.Id," : Connected"

    def on_message(self,client,userdata,message):
        print str(message.topic),"\t",str(message.payload),"\n"



if __name__ == "__main__":

    DHT11_PIN = 4     #BCM 4

    address_data = requests.get("http://192.168.137.98:8080/AddressServer/get")
    ip,port = json.loads(address_data.text)['ip'],json.loads(address_data.text)['port']
    url = "http://"+ip+":"+port+"/catalog.json"
    r = requests.get(url+'/broker')
    broker_ip,broker_port = json.loads(r.text)['ip'],json.loads(r.text)['port']
    r_thingspeak = requests.get(url+'/topic?tp=tsa')
    Thingspeak_pubTopic = json.loads(r_thingspeak.text)['sub']

    DHT11 = DHT11_Clients("DHT11",broker_ip,"/MedicineBox/humi_temp",None)
    DHT11_thingspeak = DHT11_Clients("DHT11_thingspeak","mqtt.thingspeak.com",Thingspeak_pubTopic,None,1883)
    
    #registe this device
    url = "http://"+ip+":"+port+"/catalog.json/add/device"
    payload = {'id':"DHT11",'ip':"None",'topic':"/MedicineBox/humi_temp",'resource':'humidity and temperature'}
    requests.post(url,payload)

    DHT11.start_loop()
    DHT11_thingspeak.start_loop()

    try:
        while True :
            humidity,temp = ada.read_retry(11,DHT11_PIN)
            payload = json.dumps({'temp':temp,'humidity':humidity})
            payload_thingspeak = "field1="+str(humidity)+"&field2="+str(temp)+"&status=MQTTPUBLISH"
            DHT11.publish(payload)
            DHT11_thingspeak.publish(payload_thingspeak)
            time.sleep(1)
    except KeyboardInterrupt:
        print "exiting"
        DHT11.stop_loop()
        DHT11_thingspeak.stop_loop()








































