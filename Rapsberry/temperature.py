import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import datetime

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

#read data using pin 14
sensor = Adafruit_DHT.DHT11
pin=17

while True:
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    print("Last valid input: "+ str(datetime.datetime.now()))
    print("Temperature: %d C" % temperature)
    print("Humidity: %d "% humidity)
    time.sleep(1)