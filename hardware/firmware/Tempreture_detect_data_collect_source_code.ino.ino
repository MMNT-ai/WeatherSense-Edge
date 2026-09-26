#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT11
#define LDRPIN A0

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  int lightIntensity = analogRead(LDRPIN);

  if (isnan(humidity) || isnan(temperature)) {
    Serial.print("DHT Sensor Error! - Light reading: ");
    Serial.println(lightIntensity);
  } else {
    // Format: Temperature,Humidity,LightIntensity
    Serial.print(temperature);
    Serial.print(",");
    Serial.print(humidity);
    Serial.print(",");
    Serial.println(lightIntensity);
  }

  delay(2000); 
}