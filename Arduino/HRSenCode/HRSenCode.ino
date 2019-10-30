#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include "HeartSpeed.h"

HeartSpeed heartspeed(A1);           ///Arduino Port for HR Sensor
// MQTT
// MAC
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
// Server IP 
const char* server = "192.168.1.7";
// Topic 
const char* topicName = "/BPM";

int valor;

//REST
// Server IP 
char servidor[] = "192.168.1.123";    // Address Manager Server IP
// Port
int port=8282;
IPAddress ip(192, 168, 0, 177);     //Arduino Default IP
EthernetClient ethClient;
PubSubClient MQTTClient(ethClient);

void mycb(uint8_t rawData, int value)
{
  if(rawData){
    Serial.println(value);
  }else{
    Serial.print("HeartRate Value = "); Serial.println(value);
  }
  valor=value;
  Con(valor);
}

void setup() {
  Serial.begin(115200);

  heartspeed.setCB(mycb);    

  heartspeed.begin();
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    // try to congifure using IP address instead of DHCP:
    Ethernet.begin(mac, ip);
  }
  // give the Ethernet shield a second to initialize:
  delay(1000);
  Serial.println("Connecting...");
  MQTTClient.setServer(server, 1883);
  RE();

}
void Con(int HR){
  String Valo;
  String msg;
  if (!MQTTClient.connected()) {
    Serial.print("Connecting ...\n");
    MQTTClient.connect("Arduino Client");
  }
  else {
    // Envio
    char buffer[10];
    dtostrf(HR,0, 0, buffer);
    MQTTClient.publish(topicName, buffer);

  }
  // Tiempo entre envios (en ms)
  delay(100);
}

void RE(){
  // if you get a connection, report back via serial:
  if (ethClient.connect(servidor, port)) {
    Serial.println("connected");
    // Make a HTTP request:
    ethClient.println("POST /catalog/add_device?json_msg={'ID':'ARS01','end_point':['/ARS01/BPM'],'resources':['BPM']} HTTP/1.1");
    ethClient.println("Host: 192.168.1.193");
    ethClient.println("Content-Length: 0");
    ethClient.println("Connection: close");
    ethClient.println();
    Serial.println("Device Registered");
  } else {
    // if you didn't get a connection to the server:
    Serial.println("connection failed");
  }

}

void RES(){
  // if you get a connection, report back via serial:
  if (ethClient.connect(servidor, port)) {
    Serial.println("connected");
    // Make a HTTP request:
    ethClient.println("PUT /catalog/refresh?ID=AR01 HTTP/1.1");
    ethClient.println("Host: 192.168.1.193");
    ethClient.println("Content-Length: 0");
    ethClient.println("Connection: close");
    ethClient.println();
    Serial.println("Device Refresh");
  } else {
    // if you didn't get a connection to the server:
    Serial.println("connection failed");
  }
}

void loop() { 

  // if the server's disconnected, stop the client:
  if (!ethClient.connected()) {
    Serial.println();
    Serial.println("disconnecting.");
    ethClient.stop();
    
}

delay(1000);

}
