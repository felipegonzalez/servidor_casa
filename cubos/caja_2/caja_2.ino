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
}

void loop() {
  
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
  delay(1000);

  sensors_event_t event;
  bmp.getEvent(&event);
   /* Display the results (barometric pressure is measure in hPa) */
  if (event.pressure)
  {
    /* Display atmospheric pressue in hPa */
    Serial.print("pressure,hPa,1,");
    Serial.println(bmp.seaLevelForAltitude(2243, event.pressure));
    //Serial.println(" hPa");
    
    /* Calculating altitude with reasonable accuracy requires pressure    *
     * sea level pressure for your position at the moment the data is     *
     * converted, as well as the ambient temperature in degress           *
     * celcius.  If you don't have these values, a 'generic' value of     *
     * 1013.25 hPa can be used (defined as SENSORS_PRESSURE_SEALEVELHPA   *
     * in sensors.h), but this isn't ideal and will give variable         *
     * results from one day to the next.                                  *
     *                                                                    *
     * You can usually find the current SLP value by looking at weather   *
     * websites or from environmental information centers near any major  *
     * airport.                                                           *
     *                                                                    *
     * For example, for Paris, France you can check the current mean      *
     * pressure and sea level at: http://bit.ly/16Au8ol                   */
    float temperature;
    bmp.getTemperature(&temperature);
    Serial.print("temperature,C,1,");
    Serial.println(temperature);
    //Serial.println(" C");

    /* Then convert the atmospheric pressure, and SLP to altitude         */
    /* Update this next line with the current SLP for better results      */
    float seaLevelPressure = SENSORS_PRESSURE_SEALEVELHPA;
    Serial.print("altitude,m,1,"); 
    Serial.println(bmp.pressureToAltitude(seaLevelPressure,
                                        event.pressure)); 
    
    //Serial.println(" m");
    //Serial.println("");     
  }
  else
  {
    Serial.println("Sensor error");
  }
  delay(1000);

}