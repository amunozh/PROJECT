import time
import os 
import serial
import subprocess
import numpy as np
import paho.mqtt.client as paho
import json
import senMsg as sm
import requests
import socket
from datetime import datetime
import fcntl
import sys
from LCD05_16 import LCD05_162
import struct



class Clients(object):

    def __init__(self,ID,broker,sub_topic,pub_topic,port=None):
        self.Id = ID
        self.broker = broker
        self.port = port
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.client = paho.Client(ID)
        self.client.on_disconnect = self.on_disconnect
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
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
        
    def set_actuator(self,actuator_port):
        self.serial_output = serial.Serial(port=actuator_port,baudrate=9600)
        
    def publish(self,payload,QOS=0):
        self.client.publish(self.pub_topic,payload,QOS)

    def subscribe(self,QOS=2):
        self.client.subscribe(self.sub_topic,QOS)

    def on_connect(self,client,userdata,flags,rc):
        print(self.Id," : Connected")
        self.flag_connected = True
     
    def on_disconnect(self,client,userdata,rc):
        print(self.Id," : Disconnected")
        self.flag_connected = False   
    
    def on_message(self,client,userdata,message):
        # incoming data is encoded to bytes, need tp decode
        data = json.loads(message.payload.decode())
        print(data)
        if int(data['on'])==1:
            speed = 200
            speed_bytes = b'%d' %speed
            self.serial_output.write(speed_bytes)
        else:
            speed = 0
            speed_bytes = b'%d' %speed
            self.serial_output.write(speed_bytes)



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
#                sub_topic = get_MQTTtopic(hotspot_ip,'analysis')
#                if sub_topic.status_code != 200 or pub_topic.status_code != 200:
#                    continue
#                else:
#                    break

            sub_topic = "/test2"
            pub_topic = "/test"
        except Exception as e:
            print(e)
            time.sleep(4)
            continue
        while True:
            mqtt_client = Clients("Indoor",hotspot_ip,sub_topic,pub_topic)
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
                    with open("/home/pi/code/port.json") as f:
                        content = json.loads(f.read())
                    if content["indoor"] != 0:
                        indoor_port = content["indoor"]
                    else:
                        serial_port1 = []
                        output = str(subprocess.check_output(["ls /dev/tty*"],shell=True))
                        output_list = output.split("\\n")
                        for i in output_list:
                            if "ACM" in i:
                                serial_port1.append(i)
                        if len(serial_port1) == 0:
                            print("No Arduino")
                            time.sleep(1)
                        else:
                        # find indoor arduino
                            for i in serial_port1:
                                if len(serial_port1) == 2:
                                    if i == content['outdoor']:
                                        pass
                                    elif content['outdoor'] != 0:
                                        indoor_port = i
                                        break
                                serial_reading = serial.Serial(port=i,baudrate=9600)
                                data = str(serial_reading.readline().decode("utf-8")).split(",")
                                if data[0] == '1':
                                    indoor_port = i
                                    with open("/home/pi/code/port.json") as f:
                                        content = json.loads(f.read())
                                    content['indoor'] = i
                                    with open("/home/pi/code/port.json","w") as f:
                                        f.write(json.dumps(content))
                                    break
                            try:
                                indoor_port
                            except NameError:
                                print("Don't find indoor Arduino")
                                time.sleep(1)
                                continue
                            mqtt_client.set_actuator(indoor_port)
                            mqtt_client.subscribe()
                            print("subscribe")
                            break
                except KeyboardInterrupt:
                    mqtt_client.stop_loop()
                    try:
                        del indoor_port
                    except:
                        pass
                    with open("/home/pi/code/port.json") as f:
                        content = json.loads(f.read())
                    content['indoor'] = 0
                    with open("/home/pi/code/port.json","w") as f:
                        f.write(json.dumps(content))
                    sys.exit("KeyboardInterrupt")
            try:   
                while True:
                    serial_reading = serial.Serial(port=indoor_port,baudrate=9600)
                    data = str(serial_reading.readline().decode("utf-8")).split(",")
                    humi,temp,pressure,tvoc,co2 = data[1],data[2],data[3],data[4],data[5]                  

                    msg = sm.senMsg("indoor",datetime.utcnow())
                    msg.addSensor("temp","C",temp)
                    msg.addSensor("humi","%",humi)
                    msg.addSensor("tvoc","ppm",tvoc)
                    msg.addSensor("co2","ppm",co2)
                    msg.addSensor("pressure","hPa",pressure)
                    msg = msg.toJson()

                    mqtt_client.publish(msg)
                    
                    
#                    lcd.clear_row(0)
#                    lcd.write("indoor CO2 "+str(data[-1]).split("=")[1],0,1)#+","+data[11:16]+","+data[29:34])
                    print(data)
                    time.sleep(0.1)
            except KeyboardInterrupt:  
#                lcd.clear_row(0)
                mqtt_client.stop_loop() 
                try:
                    del indoor_port
                except:
                    pass
                with open("/home/pi/code/port.json") as f:
                    content = json.loads(f.read())
                content['indoor'] = 0
                with open("/home/pi/code/port.json","w") as f:
                    f.write(json.dumps(content))
                sys.exit("KeyboardInterrupt")
        except Exception as e:
            print(e)
            if mqtt_client.flag_connected:
                mqtt_client.stop_loop()
#            lcd.clear_row(0)
            try:
                del indoor_port
            except:
                pass
            with open("/home/pi/code/port.json") as f:
                content = json.loads(f.read())
            content['indoor'] = 0
            with open("/home/pi/code/port.json","w") as f:
                f.write(json.dumps(content))
            time.sleep(2)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            