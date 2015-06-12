#include <Console.h>
#include <Bridge.h>
#include <YunServer.h>
#include <YunClient.h>
#include "DHT.h"
#define DHTTYPE DHT22
const int vaneValues[] PROGMEM={62, 80, 90, 121, 179,238,278,395,450,584,614,686,767,809,868,925};
const int vaneDirections[] PROGMEM={2925,2475,2700,3375,3150,225, 0, 2025,2250, 675,450,1575,1800,1125,1350,900};

const float distPerClick = 11.781;
Process time_lx;
int hours, minutes, seconds, prev_hours;  


volatile unsigned long count_anem = 0;
volatile unsigned long last_anem = 0;
volatile unsigned long count_rain = 0;
volatile unsigned long last_rain = 0;

const int anemoLedPin = 10; // the pin that the LED is attached to
const int vaneLedPin = 6;
const int dhtPin = 2;

DHT dht(dhtPin, DHTTYPE);

const int anemoPin = 3;
const int vanePin = 5;
const int rainfallPin = 7;
int estado = 0;
int incomingByte;      // a variable to read incoming serial data into
unsigned long time;
unsigned long time2;
unsigned long time3;
unsigned long time_dht;
float humidity = 0;
float temperature = 0;
unsigned long time_rep;
unsigned long time_rep_r;
float temperature_latest=0;
float humidity_latest=0;
double wind_latest=0;
double vane_latest=0;
double rain_latest=0;
String timeString;
YunServer server;

void setup() {
  // initialize serial communication:
  Bridge.begin();
 //Console.begin(); 
  dht.begin();
  //while (!Console){
  //  ; // wait for Console port to connect.
  //}
  //Console.println("You're connected to the Console!!!!");
  pinMode(anemoLedPin, OUTPUT);
  analogWrite(anemoLedPin, LOW);
  time = millis();
  time2 = millis();
  time3 = millis();
  time_dht = millis();

  time_rep = millis();
  
  //server.listenOnLocalhost();
  server.begin();
  
  attachInterrupt(0, anemometerClick, FALLING);
  attachInterrupt(4, rainfallClick, FALLING);
  prev_hours=0;

}

void loop() {
  
  // Find out time
  time_lx.begin("date");
  time_lx.addParameter("+%T");
  time_lx.run();
  timeString = "";
   while(time_lx.available()) {
        char c = time_lx.read();
        timeString += c;
     }
   hours = timeString.substring(0, timeString.indexOf(":")).toInt();
   if(prev_hours != hours){
     //reset rain count
     count_rain = 0;
   }
  int prev_hours = hours;
  YunClient client = server.accept();
  if(client){
    process(client);
    client.stop();
  }
  delay(50);

      
 if(millis()-time_dht > 5000){
   humidity_latest = dht.readHumidity();
   temperature_latest = dht.readTemperature();
   time_dht = millis();
  //Console.print("Humidity: ");
  //Console.println(humidity_latest);
  //Console.print("Temperature: ");
  //Console.println(temperature_latest);
 }
 
  if(millis() - time_rep > 1000){
    wind_latest = getUnitWind();
    time_rep = millis();
    vane_latest = getVane();         
  }
  if(millis() - time_rep_r > 1000*10){
    Console.print("Rainfall (mm/h):");
    rain_latest = getRainfall();
    //Console.println(rain_latest);
    time_rep_r = millis();
  }
  
  
}


void anemometerClick()
{
  long diff_anem = micros() - last_anem;
  last_anem = micros();
  if(diff_anem > 500) {
    count_anem++;
  }
}

void rainfallClick(){
  long diff_rain = micros() - last_rain;
  last_rain = micros();
  if(diff_rain > 500){
    count_rain++;
  }
}

double getUnitWind()
{
  unsigned long count_current = count_anem;
  count_anem = 0;
  unsigned long time_actual = time2;
  time2 = millis();
  double diff_t = ((millis() - time_actual)/1000.0)/3600.0;
  return((distPerClick*count_current/100000)/(diff_t));

}

double getRainfall()
{
  unsigned long count_current_r = count_rain;
  
  //count_rain = 0;
  //unsigned long time_actual = time3;
  //time3 = millis();
  //double diff_t = ((millis() - time_actual)/1000.0)/3600.0;
  //return((0.2794*count_current_r)/(diff_t));
   return(0.2794*count_current_r);
}

double getVane() {
    unsigned int reading = analogRead(vanePin);
    unsigned int lastDiff=2048;

    for (int n=0;n<16;n++) {
      int diff = reading - pgm_read_word(&vaneValues[n]);
      diff = abs(diff);
      if(diff==0)
         return pgm_read_word(&vaneDirections[n])/10.0;
      if(diff > lastDiff){
        return pgm_read_word(&vaneDirections[n-1])/10.0;
      }
     lastDiff=diff;
   }
 
  return pgm_read_word(&vaneDirections[15])/10.0;

  
}


void process(YunClient client) {
  
  Process date;
  date.runShellCommand("date");
  String timeString_req = "";
   while(date.available()) {
        char c = date.read();
        if(c != 13 & c!=3 & c!=12){
          timeString_req += c;
        }
     }
      //client.println(timeString);
      //client.println(hours);
  String command = client.readStringUntil('/');
  //client.println(command);
  if (command == "weather"){
    client.print("{ 'date':'");
    timeString_req.trim();
    client.print(timeString_req);
    client.print("',");
    client.print(" 'temperature':'");
    client.print(temperature_latest);
    client.print("',");
     client.print("'humidity':'");
    client.print(humidity_latest);
     client.print("',");
     client.print("'wind_direction':'");
     client.print(vane_latest);
      client.print("',");
      client.print("'wind_speed':'");
 
        client.print(wind_latest);
              client.print("',");
      client.print("'rain_mm_day':'");
            client.print(rain_latest);  
     client.println("'}");
    
  }
  
  
  if (command == "temp"){
    client.print("Temperature = ");
    client.println(temperature_latest);
    
  }
    if (command == "humidity"){
    client.print("Humidity = ");
    client.println(humidity_latest);
    
  }
  if (command == "vane") {
        client.println(vane_latest);
  }
    if (command == "wind-speed") {
        client.println(wind_latest);
  }
  if (command == "rainfall"){
            client.println(rain_latest);  
  }
}
