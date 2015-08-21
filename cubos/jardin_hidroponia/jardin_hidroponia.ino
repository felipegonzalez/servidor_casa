
#define FILL_PIN 4
#define FLOW_PIN 2
#define PH_PIN 5


volatile uint16_t pulses = 0;
volatile uint8_t lastflowpinstate;
volatile uint32_t lastflowratetimer = 0;
volatile float flowrate;
unsigned long time_send;



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
  Serial.begin(9600);
  pinMode(FLOW_PIN, INPUT);
  digitalWrite(FLOW_PIN, HIGH);
  lastflowpinstate = digitalRead(FLOW_PIN);
  useInterrupt(true);
  time_send = millis();

}

void loop(void)
{       
     if(abs(millis() - time_send) > 5000){
        time_send = millis();
        int fill_read = digitalRead(FILL_PIN);
        int ph_analog = analogRead(PH_PIN);      
        float ph_read = 4.0 + ((float)ph_analog - 284.0)*0.01515;
        //flowrate  
        Serial.print("lleno, binary,1,");
        Serial.println(fill_read);
        Serial.print("ph_probe, pH,1, ");
        Serial.println(ph_read);
        Serial.print("flujo, litros,1, ");
        Serial.println(flowrate);
     }
}

