import paho.mqtt.client as PahoMQTT
import time
import json


class MyPublisher:
    def __init__(self, clientID):
        self.clientID = clientID
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
    def start (self):
        #manage connection to broker
        #self._paho_mqtt.username_pw_set('user1','user1')
        self._paho_mqtt.connect('192.168.1.18', 1883)
        self._paho_mqtt.loop_start()
    def stop (self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
    
    def myPublish(self, topic, message):
        # publish a message with a certain topic
        self. _paho_mqtt.publish(topic, message, 0)
    
    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to message broker with result code: "+str(rc))



if __name__ == "__main__":
    test = MyPublisher("MyPublisher")
    test.start()

    a = 0
    while (a < 30):
        message = json.dumps({'temp':a})
        print ("Publishing: '%s'" % (message))
        test.myPublish ('/this/topic', message)
        a += 1
        time.sleep(1)

    test.stop()


