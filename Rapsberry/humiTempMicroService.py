import paho.mqtt.client as paho
import json
import time
import requests
import Adafruit_DHT as ada

#from datetime import datetime


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

    
def read_file(file):
    
    lineDeg= [0]
        
    with open(file) as f:
        for i in range(len(lineDeg)):
            lineDeg[i]=f.readline()        
    f.close()
    str0= ''.join(lineDeg)
        
    return (str0)


if __name__ == "__main__":

    DHT11_PIN = 17     #BCM 17

    address_data = requests.get("http://192.168.1.122:8181/address_manager/get")
    print(address_data)
    ip,port = json.loads(address_data.text)['ip'],str(json.loads(address_data.text)['port'])
    
    url = "http://"+ip+":"+port+"/catalog"
    print(url)
    r = requests.get(url+'/broker')
    print(r.text)
    broker_ip,broker_port = json.loads(r.text)['ip'],str(json.loads(r.text)['port'])
    
    
    DHT11 = DHT11_Clients("DHT11",broker_ip,"/RPS01/humi_temp",None)
    
    #registe this device
    payload = json.dumps({'ID':'RPS01','end_point':['/RPS01/humi_temp',None],'resources':'humidity&temperature'})
    url = "http://"+ip+":"+port+"/catalog/add_device?json_msg="+payload
    requests.post(url)
    
    DHT11.start_loop()

    try:
        while True :
            humidity,temp = ada.read_retry(ada.DHT11,DHT11_PIN)
            url = "http://"+ip+":"+port+"/catalog/refresh?ID=RPS01"
            DHT11.publish(json.dumps({'bn':"RPS01",'e':[{'n':'humidity','u':'%','t':time.time(),'v':humidity},{'n':'temperature','u':'cel','t':time.time(),'v':temp}]}))
            time.sleep(1)

    except KeyboardInterrupt:
        print "exiting"
        DHT11.stop_loop()
       
    








































