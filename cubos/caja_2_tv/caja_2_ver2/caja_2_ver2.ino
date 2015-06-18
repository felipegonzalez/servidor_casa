/**************************************************************************/
/*!
This is a demo for the Adafruit MCP9808 breakout
----> http://www.adafruit.com/products/1782
Adafruit invests time and resources providing this open source code,
please support Adafruit and open-source hardware by purchasing
products from Adafruit!
*/
/**************************************************************************/
#include <Wire.h>
#include "Adafruit_MCP9808.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP085_U.h>

// Create the MCP9808 temperature sensor object
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();
Adafruit_BMP085_Unified bmp = Adafruit_BMP085_Unified(10085);
int photo_pin =1;
int pir_pin1 =7;
int pir_pin2 =6;
long tiempo_actual;
long tiempo_ultima;
long tiempo_ultima_bp;
long tiempo_pir_1;
long tiempo_pir_2;

void setup() {
  Serial.begin(9600);
  //Serial.println("MCP9808 demo");
  
  // Make sure the sensor is found, you can also pass in a different i2c
  // address with tempsensor.begin(0x19) for example
  if (!tempsensor.begin()) {
    Serial.println("Couldn't find MCP9808!");
    while (1);
  }
    /* Initialise the sensor */
  if(!bmp.begin())
  {
    /* There was a problem detecting the BMP085 ... check your connections */
    Serial.println("Ooops, no BMP085 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  	tiempo_ultima = millis();
    tiempo_ultima_bp = millis();
    tiempo_actual = millis();
    tiempo_pir_1 = millis();
    tiempo_pir_2 = millis();

}

void loop() {
  tiempo_actual = millis();
  int pirread1 = digitalRead(pir_pin1);
  int pirread2 = digitalRead(pir_pin2);

  if(pirread1 > 0){
  	if(tiempo_actual >= tiempo_pir_1 + 2000){
      		tiempo_pir_1 = millis();
      		//tiempo_ultima = millis();
      		registro_enviar_pir();
    	}
  }
  if(pirread2 > 0){
  	if(tiempo_actual >= tiempo_pir_2 + 2000){
      		tiempo_pir_2 = millis();
      		//tiempo_ultima = millis();
      		registro_enviar_pir();
    	}
  }

  if(tiempo_actual >= tiempo_ultima + 20000){
    registro_enviar();
    tiempo_ultima = millis();
  }
  if(tiempo_actual >= tiempo_ultima_bp + 25000){
    registro_enviar_bmp();
    tiempo_ultima_bp = millis();
  }
}

void registro_enviar(){
  int photoread = analogRead(photo_pin);  
  int pirread1 = digitalRead(pir_pin1);
  int pirread2 = digitalRead(pir_pin2);
  
  Serial.print("photo,analog,1,");
  Serial.println(photoread);
  Serial.print("pir,binary,1,");
  Serial.println(pirread1);
  Serial.print("pir,binary,2,");
  Serial.println(pirread2);
  float c = tempsensor.readTempC();
  Serial.print("temperature,C,2,"); 
  Serial.println(c);
}

void registro_enviar_bmp(){
  sensors_event_t event;
  bmp.getEvent(&event);
   /* Display the results (barometric pressure is measure in hPa) */
  if (event.pressure)
  {
    /* Display atmospheric pressue in hPa */
    Serial.print("pressure,hPa,1,");
    Serial.println(bmp.seaLevelForAltitude(2243, event.pressure));
    float temperature;
    bmp.getTemperature(&temperature);
    Serial.print("temperature,C,1,");
    Serial.println(temperature);
    float seaLevelPressure = SENSORS_PRESSURE_SEALEVELHPA;
    Serial.print("altitude,m,1,"); 
    Serial.println(bmp.pressureToAltitude(seaLevelPressure,
                                        event.pressure)); 
    
    //Serial.println(" m");
    //Serial.println("");     
  }
  else
  {
    //Serial.println("Sensor error");
  }

}


void registro_enviar_pir(){
  int photoread = analogRead(photo_pin);  
  int pirread1 = digitalRead(pir_pin1);
  int pirread2 = digitalRead(pir_pin2);
  
  Serial.print("photo,analog,1,");
  Serial.println(photoread);
  Serial.print("pir,binary,1,");
  Serial.println(pirread1);
  Serial.print("pir,binary,2,");
  Serial.println(pirread2);
 

}