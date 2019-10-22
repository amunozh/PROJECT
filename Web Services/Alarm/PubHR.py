# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 00:34:10 2019

@author: Miguel
"""

import time
import paho.mqtt.client as paho
import json

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
 
client = paho.Client("prueba2")
client.on_publish = on_publish
client.connect("192.168.1.6", 1883)
client.loop_start()

   
F=0
HR=30

while (F<=10):
    # Cont=json.dumps({'Heart Rate':HR})
    Cont = json.dumps(HR)
    (rc, mid) = client.publish("/ARS01/BPM", Cont, qos=0)
    HR=HR+10
    F=F+1
    time.sleep(10)

