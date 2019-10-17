import paho.mqtt.client as PahoMQTT
import time


class MySubscriber:
		def __init__(self, clientID):
			self.clientID = clientID
			# create an instance of paho.mqtt.client
			self._paho_mqtt = PahoMQTT.Client(clientID, False) 

			# register the callback
			self._paho_mqtt.on_connect = self.myOnConnect
			self._paho_mqtt.on_message = self.myOnMessageReceived

			self.topic = '/RPS02/beacon'


		def start (self):
			#manage connection to broker
            #client.username_pw_set('rdehsovk', 'yWMIkwY8dkw1')
			self._paho_mqtt.connect('192.168.1.6', 1883)
			self._paho_mqtt.loop_start()
			# subscribe for a topic
			self._paho_mqtt.subscribe(self.topic, 2)

		def stop (self):
			self._paho_mqtt.unsubscribe(self.topic)
			self._paho_mqtt.loop_stop()
			self._paho_mqtt.disconnect()

		def myOnConnect (self, paho_mqtt, userdata, flags, rc):
			print ("Connected to message broker with result code: "+str(rc))

		def myOnMessageReceived (self, paho_mqtt , userdata, msg):
			# A new message is received
			print ("Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'")



if __name__ == "__main__":
	test = MySubscriber("MySubscriber1")
	test.start()

	a = 0
	while (a < 30):
		a += 1
		time.sleep(1)

	test.stop()
