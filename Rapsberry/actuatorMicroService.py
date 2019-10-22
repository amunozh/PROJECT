import RPi.GPIO as GPIO     # Importing RPi library to use the GPIO pins
from time import sleep  # Importing sleep from time library
import random
import string
import cherrypy
import socket
import requests
import json

class serviceLed(object):
    exposed=True
    #@cherrypy.expose
    def __init__(self):
        pass

    #@cherrypy.expose
    def GET(self, *uri, **params):
        
        if uri[0] == 'cold':

            led_pin=27
            GPIO.setmode(GPIO.BCM)          # We are using the BCM pin numbering
            GPIO.setup(led_pin, GPIO.OUT)   # Declaring pin 21 as output pin

            pwm = GPIO.PWM(led_pin, 100)    # Created a PWM object
            pwm.start(0)                    # Started PWM at 0% duty cycle
            value=params["intensity"]
            
            for x in range(10):
                
                pwm.ChangeDutyCycle(int(value)) # Change duty cycle
                sleep(1)         # Delay of 10mS

        elif uri[0] == 'warm':
            led_pin=21
            GPIO.setmode(GPIO.BCM)          # We are using the BCM pin numbering
            GPIO.setup(led_pin, GPIO.OUT)   # Declaring pin 21 as output pin

            pwm = GPIO.PWM(led_pin, 100)    # Created a PWM object
            pwm.start(0)                    # Started PWM at 0% duty cycle
            value=params["intensity"]
            
            for x in range(10):
            
                pwm.ChangeDutyCycle(int(value)) # Change duty cycle
                sleep(1)         # Delay of 10mS

        return str(value)


if __name__ == '__main__':
    
    conf = {'/'
        : {'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True, }}
    
    cherrypy.tree.mount(serviceLed(), '/actuator', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8080})
    
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    
    print(IPAddr)
    cherrypy.engine.start()
    cherrypy.engine.block()
    address_data = requests.get("http://192.168.1.122:8585/address_manager/get")
    
    ip,port = json.loads(address_data.text)['ip'],str(json.loads(address_data.text)['port'])

    #register
    
    payload = json.dumps({'ID':'RPA01','end_point':[None,IPAddr+":8080/actuator/"],'resources':'Actuator_temp'})
    url = "http://"+ip+":"+port+"/catalog/add_device?json_msg="+payload
    requests.post(url)

    
