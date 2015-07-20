
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define OLED_RESET 4
Adafruit_SSD1306 display(OLED_RESET);

unsigned long time_start;
unsigned long interval = 180000;
int primera = 1;
#include <EmonLib.h>
EnergyMonitor emon;

void setup() {
  
  // put your setup code here, to run once:
  //analogReference(EXTERNAL);
  Serial.begin(9600);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3D);  // initialize with the I2C addr 0x3D (for the 128x64)
   delay(2000);
  display.clearDisplay();
    display.setTextSize(1);
   display.setTextColor(WHITE);
  display.setCursor(0,0);
  display.println("Arrancando...");
  display.display();

//  emon.current(1, 111.1);
  emon.current(1, 151.0);
  emon.voltage(2, 0.95*234.26/2.0, 1.7);
  delay(2000);
  //for(int i=0; i <2; i++){
   //   double testIrms = emon.calcIrms(1480);
   //  delay(200);   
  //}
  time_start = millis();
  
}

void loop() {
  // put your main code here, to run repeatedly:
  //double Irms = emon.calcIrms(1480);
  emon.calcVI(40,5000); 
  float realPower       = emon.realPower;        //extract Real Power into variable
  float apparentPower   = emon.apparentPower;    //extract Apparent Power into variable
  float powerFactor     = emon.powerFactor;      //extract Power Factor into Variable
  float supplyVoltage   = emon.Vrms;             //extract Vrms into Variable
  float Irms            = emon.Irms;             //extract Irms into Variable
  //double w_apparent = 120*Irms;
  
  //Serial.println(analogRead(1));

  display.clearDisplay();
  display.setCursor(0,0);
  display.print("Voltios: ");
  display.println(supplyVoltage);
  display.print("Amps: ");
  display.println(Irms);
  display.print("Potencia real: ");
  display.println(realPower);
  display.print("Fctr potencia: ");
  display.println(powerFactor);
  //display.print("Amps: ");
  //display.println(Irms);
  //  display.print("Watts: ");
  //display.println(w_apparent);
  unsigned long time_now = millis();
  Serial.println(time_now-time_start);
  display.println(time_now-time_start);
  if((time_now - time_start) > interval || primera == 0){
    primera=0;
    display.println("Transmitiendo...");
    Serial.print("ct,A,1,");
    Serial.println(Irms);
    Serial.print("ct,kW,1,");
    Serial.println(realPower/1000.0); 
  }
  //emon.serialprint();
  
  //display.println("Sending...");
  display.display();
  delay(5000);

}
