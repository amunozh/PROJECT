import time
import os 
import serial
import subprocess
import numpy as np
import paho.mqtt.client as paho
import json
import requests
from datetime import datetime
import senMsg as sm
import socket
from LCD05_16 import LCD05_162
import fcntl
import sys
import struct



class Clients(object):

    def __init__(self,ID,broker,pub_topic,port=None):
        self.Id = ID
        self.broker = broker
        self.port = port
        self.pub_topic = pub_topic
        self.client = paho.Client(ID)
        self.client.on_disconnect = self.on_disconnect
        self.client.on_connect = self.on_connect
        self.flag_connected = False

    def start_loop(self):   
        if self.port == None:
            self.client.connect(self.broker)
        else:
            self.client.connect(self.broker,self.port)
        self.client.loop_start()

    def stop_loop(self):
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self,payload,QOS=0):
        self.client.publish(self.pub_topic,payload,QOS)

    def on_connect(self,client,userdata,flags,rc):
        print(self.Id," : Connected")
        self.flag_connected = True
     
    def on_disconnect(self,client,userdata,rc):
        print(self.Id," : Disconnected")
        self.flag_connected = False   




def get_ip_address(ifname):
    """
        get the IP address of ethernet or WiFi
        ifname = "eth0": get IP address of ethernet
        ifname = "wlan0": get IP address of WiFi/Hotspot
        Return type: String   (eg."192.168.37.24")
    """
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                            0x8915,
                            struct.pack('256s',bytes(ifname[:15],'utf-8'))
                         )[20:24])



def get_MQTTtopic(ip,service,port=8080):
    """
        return MQTT topic of different service    
    """
    url = "http://"+ip+":"+str(port)+"/"   
    
    if service == "mongoDB":
        request = requests.get(url+"uri,params")
    if service == "mobile_app":
        request = requests.get(url+"uri,params")
    if service == "analysis":    
        request = requests.get(url+"uri,params")              
    topic = json.load(request.text)['topic']
    return topic




if __name__ == "__main__":


    while True:
        try:
            hotspot_ip = get_ip_address('wlan0')
                      
            # Get the topic of MongoDB/Mobile APP/Analysis.
#            while True:
#                pub_topic = get_MQTTtopic(hotspot_ip,'mongoDB')
#                if pub_topic.status_code != 200:
#                    continue
#                else:
#                    break

            pub_topic = "Readings/ext/SS2"
        except Exception as e:
            print(e)
            time.sleep(4)
            continue
        while True:
            mqtt_client = Clients("outdoor","192.168.12.191",pub_topic)
            try:
#                lcd = LCD05_162()
                mqtt_client.start_loop()
                break
            except Exception as e:
                print(e)
                time.sleep(5)
        try:
            while True:
                try:
                    with open("/home/pi/node/sis_backend/node/port.json") as f:
                        content = json.loads(f.read())
                    if content["outdoor"] != 0:
                        outdoor_port = content["outdoor"]
                    else:
                        serial_port2 = []
                        output = str(subprocess.check_output(["ls /dev/tty*"],shell=True))
                        output_list = output.split("\\n")
                        for i in output_list:
                            if "ACM" in i:
                                serial_port2.append(i)
                        if len(serial_port2) == 0:
                            print("No Arduino")
                            time.sleep(1)
                        else:
                        # find outdoor arduino
                            list.reverse(serial_port2)
                            for i in serial_port2:
                                if len(serial_port2) == 2:
                                    if i == content['indoor']:
                                        pass
                                    elif content['indoor'] != 0:
                                        outdoor_port = i
                                        break
                                serial_reading = serial.Serial(port=i,baudrate=9600)
                                data = str(serial_reading.readline().decode("utf-8")).split(",")
                                if data[0] == '0':
                                    outdoor_port = i
                                    with open("/home/pi/node/sis_backend/node/port.json") as f:
                                        content = json.loads(f.read())
                                    content['outdoor'] = outdoor_port
                                    with open("/home/pi/node/sis_backend/node/port.json","w") as f:
                                        f.write(json.dumps(content))
                                    break
                            try:
                                outdoor_port
                            except NameError:
                                print("Don't find outdoor Arduino")
                                time.sleep(1)
                                continue
                            break
                except KeyboardInterrupt:
                    mqtt_client.stop_loop()
                    try:
                        del outdoor_port
                    except:
                        pass
                    with open("/home/pi/node/sis_backend/node/port.json") as f:
                        content = json.loads(f.read())
                    content['outdoor'] = 0
                    with open("/home/pi/node/sis_backend/node/port.json","w") as f:
                        f.write(json.dumps(content))
                    sys.exit("KeyboardInterrupt")
            try:   
                while True:
                    serial_reading = serial.Serial(port=outdoor_port,baudrate=9600)
                    data = str(serial_reading.readline().decode("utf-8")).split(",")
                    humi,temp,pressure,voc,co2 = data[1],data[2],data[3],data[4],data[5]                  

                    msg = sm.senMsg("SS2",datetime.utcnow())
                    msg.addSensor("temp","C",float(temp))
                    msg.addSensor("humid","%",float(humi))
                    msg.addSensor("voc","ppm",float(voc))
                    msg.addSensor("co2","ppm",float(co2))
                    msg.addSensor("press","hPa",float(pressure))
                    msg = msg.toJson()

                    mqtt_client.publish(msg)
#                    lcd.clear_row(1)
#                    lcd.write("out CO2 "+str(data[-1]).split("=")[1],1,1)#+","+data[11:16]+","+data[29:34])
                    print(data)
            except KeyboardInterrupt:  
                mqtt_client.stop_loop() 
#                lcd.clear_row(1)
                try:
                    del outdoor_port
                except:
                    pass
                with open("/home/pi/node/sis_backend/node/port.json") as f:
                    content = json.loads(f.read())
                content['outdoor'] = 0
                with open("/home/pi/node/sis_backend/node/port.json","w") as f:
                    f.write(json.dumps(content))
                sys.exit("KeyboardInterrupt")
        except Exception as e:
            print(e)
            if mqtt_client.flag_connected:
                mqtt_client.stop_loop()
#            lcd.clear_row(1)
            try:
                del outdoor_port
            except:
                pass
            with open("/home/pi/node/sis_backend/node/port.json") as f:
                content = json.loads(f.read())
            content['outdoor'] = 0
            with open("/home/pi/node/sis_backend/node/port.json","w") as f:
                f.write(json.dumps(content))
            time.sleep(2)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
