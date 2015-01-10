
#include "Adafruit_MCP9808.h"
#include "Wire.h"


 
#define PIN_GATE_IN 2
#define IRQ_GATE_IN  0
#define PIN_LED_OUT 13
#define PIN_ANALOG_IN A0
#define pir_pin 7
#define photo_pin 2
#define gas_pin 3
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();
long tiempo_actual;
long tiempo_ultima;
long tiempo_pir;
long tiempo_sonido;
int pirread = 0;
int sound_read = 0;
int sound_envelope = 0;
int bloque_enviar = 1;

void setup()
{
  Serial.begin(9600);
  if (!tempsensor.begin()) {
    Serial.println("Couldn't find MCP9808!");
    while (1);
  }
  //  Configure LED pin as output
  pinMode(PIN_LED_OUT, OUTPUT);
  pinMode(pir_pin, INPUT);
  // configure input to interrupt
  pinMode(PIN_GATE_IN, INPUT);
  attachInterrupt(IRQ_GATE_IN, soundISR, CHANGE);

  tiempo_ultima = millis();
  tiempo_actual = millis();
  tiempo_pir = millis();
  tiempo_sonido = millis();
  //tiempo_sonido = millis();
  
}

void loop() {
  tiempo_actual = millis();
  pirread = digitalRead(pir_pin);
  sound_read = digitalRead(PIN_GATE_IN);
  sound_envelope = analogRead(PIN_ANALOG_IN);
  if(pirread == 0){
        if(tiempo_actual >= tiempo_pir + 1500){
          tiempo_pir = millis();
          tiempo_ultima = millis();
          registro_enviar();
      }
  }

   if(sound_envelope > 20){
    if(tiempo_actual >= tiempo_sonido + 7000){
          tiempo_sonido = millis();
          tiempo_ultima = millis();
          registro_enviar();
      }
  }

  
  if(tiempo_actual >= tiempo_ultima + 20000){
    registro_enviar();
    tiempo_ultima = millis();
  }
}

void registro_enviar(){
  int photoread = analogRead(photo_pin);  
  float ctemp = tempsensor.readTempC();
  int gas_read = analogRead(gas_pin);
  
  Serial.print("pir,binary,1,");
  Serial.println(1-pirread);
  Serial.print("det_snd,binary,1,");
  Serial.println(sound_read);   
  Serial.print("lev_snd,binary,1,");
  Serial.println(sound_envelope); 
  Serial.print("photo,analog,1,");
  Serial.println(photoread);  

  delay(1000);
  //if(bloque_enviar==1){

  //} else {
    Serial.print("temperature,C,1,"); 
    Serial.println(ctemp);
    Serial.print("gaslpg,analog,1,");
    Serial.println(gas_read);  
  //}
  //bloque_enviar == 1 - bloque_enviar;
  
}
  
  //value = analogRead(PIN_ANALOG_IN);


  //Serial.print("Status: ");
  //if(value <= 10)
  //{
//  else if( (value > 10) && ( value <= 30) )
  

void soundISR()
{
  int pin_val;
  pin_val = digitalRead(PIN_GATE_IN);
  digitalWrite(PIN_LED_OUT, pin_val);   
}