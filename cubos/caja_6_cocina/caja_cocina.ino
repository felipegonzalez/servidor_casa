// caja_cocina.ino
#include "DHT.h"
#define dht_type DHT22
#define pin_dht 8


int photo_pin = 0;
int pir_pin = 7;
int gas_pin = 1;
int enviar_gas =1;

DHT dht(pin_dht, dht_type);
long tiempo_ultima;
long tiempo_actual;
long tiempo_pir;

void setup() {
	Serial.begin(9600);
	dht.begin();
	pinMode(pir_pin, INPUT);
	delay(5000);
	tiempo_ultima = millis();
    tiempo_actual = millis();
    tiempo_pir = millis();
}

void loop() {
	tiempo_actual = millis();

	int pir_read = digitalRead(pir_pin);
	if(pir_read > 0) {
		if(tiempo_actual >= tiempo_pir + 2000){
			tiempo_pir = millis();
			tiempo_ultima = millis();
			registro_enviar();
		}
	}
	if(tiempo_actual >= tiempo_ultima +  2500){
		  registro_enviar();
    	tiempo_ultima = millis();
	}
}

void registro_enviar(){

  if(enviar_gas==1){
    float humid = dht.readHumidity();
    float temp  = dht.readTemperature();
    int gas_read = analogRead(gas_pin);
    int pir_read = digitalRead(pir_pin);
    Serial.print("pir,binary,1,");
    Serial.println(pir_read);
    Serial.print("gaslpg,analog,1,");
    Serial.println(gas_read);   
    Serial.print("humidity,pc,1,");
    Serial.println(humid);
    Serial.print("temperature,C,1,");
    Serial.println(temp);

  } else {
    int photo_read = analogRead(photo_pin);  
    int pir_read = digitalRead(pir_pin);
  
    Serial.print("photo,analog,1,");
    Serial.println(photo_read);
    Serial.print("pir,binary,1,");
    Serial.println(pir_read);
  }
  enviar_gas = 1 - enviar_gas;
  
  
}