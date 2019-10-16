#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include "HeartSpeed.h"

HeartSpeed heartspeed(A1);           ///Arduino Port for HR Sensor
// MQTT
// MAC
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
// Server IP 
const char* server = "mqtt.eclipse.org";
// Topic 
const char* topicName = "Miguel1096/test/HR";




EthernetClient ethClient;
PubSubClient client(ethClient);

void setup() {
  Serial.begin(115200);
  /*!
   *  @brief Indstiller callback funktion.
   */
  heartspeed.setCB(mycb);    
  /*!
   *  @brief Åben puls test.
   */
  heartspeed.begin();
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
  }
  client.setServer(server, 1883);
}
void Con(int HR){
  if (!client.connected()) {
    Serial.print("Connecting ...\n");
    client.connect("Arduino Client");
  }
  else {
    // Envio
    char buffer[10];
    dtostrf(HR,0, 0, buffer);
    client.publish(topicName, buffer);
  }
  // Tiempo entre envios (en ms)
  delay(100);
}
void loop() { 
  
}
/*!
   *  @brief Print the position result.
   *  @brief chose heartspeed(A1),To view ECG.
   *  @brief chose heartspeed(A1,RAW_DATA),See heart rate value.
   */
void mycb(uint8_t rawData, int value)
{
  if(rawData){
    Serial.println(value);
  }else{
    Serial.print("HeartRate Value = "); Serial.println(value);
  }
  Con(value);
}
