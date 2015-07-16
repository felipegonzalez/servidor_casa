
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define OLED_RESET 4
Adafruit_SSD1306 display(OLED_RESET);

#define NUMFLAKES 10
#define XPOS 0
#define YPOS 1
#define DELTAY 2


#define LOGO16_GLCD_HEIGHT 16 
#define LOGO16_GLCD_WIDTH  16 



#include <EmonLib.h>
EnergyMonitor emon;

void setup() {
  // put your setup code here, to run once:
  //analogReference(EXTERNAL);
  Serial.begin(9600);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3D);  // initialize with the I2C addr 0x3D (for the 128x64)
   delay(2000);
  display.clearDisplay();
    display.setTextSize(2);
   display.setTextColor(WHITE);
  display.setCursor(0,0);
  display.println("Setting up...");
  display.display();

//  emon.current(1, 111.1);
  emon.current(1, 151.0);
  delay(2000);
  for(int i=0; i <10; i++){
      double testIrms = emon.calcIrms(1480);
     delay(200);   
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  double Irms = emon.calcIrms(1480);
  double w_apparent = 120*Irms;
  
  //Serial.println(analogRead(1));

  display.clearDisplay();
  display.setCursor(0,0);
  display.print("Amps: ");
  display.println(Irms);
    display.print("Watts: ");
  display.println(w_apparent);
  
  Serial.print("ct,A,1,");
  Serial.println(Irms);
  Serial.print("ct,W,1,");
  Serial.println(w_apparent);
  
   display.println("Sending...");
  display.display();
  
  delay(5000);
  
  


}
