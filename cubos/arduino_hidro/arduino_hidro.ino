/* 
*  Simple WiFi weather station with Arduino, the DHT11 sensor & the CC3000 chip
*  Part of the code is based on the work done by Adafruit on the CC3000 chip & the DHT11 sensor
*  Writtent by Marco Schwartz for Open Home Automation
*/

// Number of variables & functions
#define NUMBER_VARIABLES 2
#define NUMBER_FUNCTIONS 1

// Include required libraries
#include <Adafruit_CC3000.h>
#include <SPI.h>
#include <CC3000_MDNS.h>
#include <aREST.h>


// Define CC3000 chip pins
#define ADAFRUIT_CC3000_IRQ   3
#define ADAFRUIT_CC3000_VBAT  5
#define ADAFRUIT_CC3000_CS    10

// WiFi network (change with your settings !)
#define WLAN_SSID       "Niebelheim5"
#define WLAN_PASS       "valquiria"
#define WLAN_SECURITY   WLAN_SEC_WPA2

// DHT11 sensor pins
#define PH_PIN 5 
#define FILL_PIN 4
#define FLOW_PIN 2
// Create CC3000 

Adafruit_CC3000 cc3000 = Adafruit_CC3000(ADAFRUIT_CC3000_CS, 
ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT, SPI_CLOCK_DIV2);
                                         
// Create aREST instance
aREST rest = aREST();

// The port to listen for incoming TCP connections 
#define LISTEN_PORT           80

// Server instance
Adafruit_CC3000_Server restServer(LISTEN_PORT);

// DNS responder instance
MDNSResponder mdns;

// Variables to be exposed to the API
int ph;
int fill_state;
//int humidity;

unsigned long time_flow;


// count how many pulses!
volatile uint16_t pulses = 0;
// track the state of the pulse pin
volatile uint8_t lastflowpinstate;
// you can try to keep time of how long it is between pulses
volatile uint32_t lastflowratetimer = 0;
// and use that to calculate a flow rate
volatile float flowrate;
// Interrupt is called once a millisecond, looks for any pulses from the sensor!
SIGNAL(TIMER0_COMPA_vect) {
  uint8_t x = digitalRead(FLOW_PIN);
  
  if (x == lastflowpinstate) {
    lastflowratetimer++;
    return; // nothing changed!
  }
  
  if (x == HIGH) {
    //low to high transition!
    pulses++;
  }
  lastflowpinstate = x;
  flowrate = 1000.0;
  flowrate /= lastflowratetimer;  // in hertz
  lastflowratetimer = 0;
}

void useInterrupt(boolean v) {
  if (v) {
    // Timer0 is already used for millis() - we'll just interrupt somewhere
    // in the middle and call the "Compare A" function above
    OCR0A = 0xAF;
    TIMSK0 |= _BV(OCIE0A);
  } else {
    // do not call the interrupt function COMPA anymore
    TIMSK0 &= ~_BV(OCIE0A);
  }
}        



                     
void setup(void)
{ 
  
  // Start Serial
  Serial.begin(9600);
  time_flow = millis();
   pinMode(FLOW_PIN, INPUT);
   digitalWrite(FLOW_PIN, HIGH);
   lastflowpinstate = digitalRead(FLOW_PIN);
   useInterrupt(true);
   Serial.println("iniciando");
  // Expose variables to REST API
  rest.variable("ph",&ph);
  rest.variable("fill", &fill_state);
  //rest.variable("humidity",&humidity);
  
  // Set name
  rest.set_id("1");
  rest.set_name("estacion_hidroponia");
 
  
  
    
  // Initialise the CC3000 module
  if (!cc3000.begin())
  {
    while(1);
  }
Serial.println("Conectando wifi");
  // Connect to  WiFi network
  cc3000.connectToAP(WLAN_SSID, WLAN_PASS, WLAN_SECURITY);
    
  // Check DHCP
  while (!cc3000.checkDHCP())
  {
    delay(100);
  }  
  
   // Start multicast DNS responder
  if (!mdns.begin("estacion_hidroponia", cc3000)) {
    while(1); 
  }
  
  // Start server
  restServer.begin();

  displayConnectionDetails(); 
}

void loop(void)
{
  // Measure from DHT
  //temperature = (uint8_t)dht.readTemperature();
  //humidity = (uint8_t)dht.readHumidity();
  int ph_analog = analogRead(PH_PIN);
  fill_state=digitalRead(FILL_PIN);
  ph = 40 + (ph_analog - 284)*0.1515;
  
  // Handle any multicast DNS requests
  mdns.update();
  
  // Handle REST calls
  Adafruit_CC3000_ClientRef client = restServer.available();
  rest.handle(client);
  //if(millis()-time_flow > 2000){
   // fill_state = digitalRead(FILL_PIN);
    //Serial.print("Fill: ");
    //Serial.println(fill_state);
    
    //Serial.print("Pulses: ");
    //Serial.println(pulses);
    //Serial.println("Flowrate:");
    //Serial.println(flowrate);
    //time_flow =millis();
  //}
}

bool displayConnectionDetails(void)
{
  uint32_t ipAddress, netmask, gateway, dhcpserv, dnsserv;
  
  if(!cc3000.getIPAddress(&ipAddress, &netmask, &gateway, &dhcpserv, &dnsserv))
  {
    return false;
  }
  else
  {
    Serial.println(F("\nIP Addr: ")); cc3000.printIPdotsRev(ipAddress);
    return true;
  }
}

