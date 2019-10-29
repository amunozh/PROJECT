# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 00:34:10 2019

@author: Miguel
"""

import time
import paho.mqtt.client as paho
import json
from random import randint

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
 
client = paho.Client("prueba2")
client.on_publish = on_publish
client.connect("192.168.1.7", 1883)
client.loop_start()

   
F=0
HR=96

while (F<=100):
    # Cont=json.dumps({'Heart Rate':HR})
    Cont = json.dumps(HR)
    (rc, mid) = client.publish("/BPM", Cont, qos=0)
    HR=HR-randint(0,10)
    if HR<0:
        HR=0
    F=F+1
    time.sleep(1)

