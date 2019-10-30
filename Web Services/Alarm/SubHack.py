# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 00:34:10 2019

@author: Miguel
"""

import time
import paho.mqtt.client as Paho
import json

#Class in charge of Receive the Arduino Messagens and Send them with the Appropriate Data Format
class Meter(object):

    def __init__(self, name, sub_topic, pub_topic, broker):
        self.client = Paho.Client(name)
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.broker = broker
        self.client.on_message = self.on_message

    def start(self):
        self.client.connect(self.broker)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, Topic, msg):
        self.client.publish(self.pub_topic, msg, qos=0)


    def subscribe(self):
        self.client.subscribe(self.sub_topic)

    def on_message(self, client, userdata, message):
        content = json.loads(message.payload)
        #        print(content)
        print("We got a message!")
        print('Topic: %s Message: %s' % (message.topic, content))
        aux=str(content)
        Flag=json.dumps({'bn':'ARS01','e':[{'n':'BPM','u':'BPM','t':time.time(),'v':aux}]})
        print(Flag)
        Topic="/ARS01/BPM"
        if Flag!="0":
            self.publish(Topic, Flag)
            print("Publico")
        return

if __name__ == '__main__':
    c = Meter('HackBPM', '/BPM', '/ARS01/BPM', "192.168.1.7")

    c.start()
    counter = 0
    c.subscribe()
    while (True):
        time.sleep(1000)
    #c.stop()
