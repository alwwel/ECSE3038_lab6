#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <env.h>


#define lightb  2

int getWaterLevel();
int value = 0;
const int pp =40;


void setup() {
  Serial.begin(115200);
  pinMode(lightb,OUTPUT);

  WiFi.begin(Wifi_ssid,Wifi_passwd);
  while (WiFi.status()!= WL_CONNECTED){
    delay(500);
    Serial.print("*");
  }

  Serial.println("");
  Serial.print("Connected to WiFi");
  Serial.println(WiFi.localIP());
}

  HTTPClient http;
  
  http.begin("http://127.0.0.1/tank");
  
  http.addHeader("Content-Type", "application/json");
  char output[128];
  const size_t CAPACITY = JSON_OBJECT_SIZE(3);
  StaticJsonDocument<CAPACITY> doc;

  doc["tank_id"].set(WiFi.macAddress());
  doc["water_level"].set(value);
  
  serializeJson(doc,output);
  int httpResponseCode = http.POST(String(output));
  String payload = "{}"; 
  if (httpResponseCode>0) {
    payload = http.getString();
  }
  else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
    }
  Serial.println(payload);
  delay(2500);
  http.end();
}

void loop() {
  value=getWaterLevel();

  if(value>=60 && value<=100){
    digitalWrite(BLED,HIGH);
  }else{
    digitalWrite(BLED,LOW);
  }

int getwLevel(){
  float val = analogRead(pp);
  val=round(((val/4095)*5)/0.01);
  return val;
}