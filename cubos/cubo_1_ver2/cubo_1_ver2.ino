
#include "DHT.h"
#include <Servo.h>

// cubo_sensor_gral.ino
#define dht_type DHT22
#define pin_dht 3
#define pin_pir 4
#define pin_photo 1

Servo myservo;

int photo;
float humid;
float temp;
int motion;
long tiempo_actual;
long tiempo_ultima;
long tiempo_pir;

DHT dht(pin_dht, dht_type);

void setup() {
	dht.begin();
	pinMode(pin_pir, INPUT);
	delay(3000);
	Serial.begin(9600);
	//myservo.attach(12);
	tiempo_ultima = millis();
    tiempo_actual = millis();
    tiempo_pir = millis();
}

void loop() {
	//delay(1000);
	motion = digitalRead(pin_pir);
	tiempo_actual = millis();
	if(motion==1){
    	if(tiempo_actual >= tiempo_pir + 2000){
      		tiempo_pir = millis();
      		tiempo_ultima = millis();
      		registrar_enviar();
    	}
  	}
  	if(tiempo_actual >= tiempo_ultima + 20000){
    	registrar_enviar();
    	tiempo_ultima = millis();
  	}
 }

void registrar_enviar() {
	motion = digitalRead(pin_pir);
	photo = analogRead(pin_photo);
	humid = dht.readHumidity();
 	temp  = dht.readTemperature();
 	//Serial.println("Lecturas: ");
 	Serial.print("pir,binary,1,");
 	Serial.println(motion);
 	Serial.print("photo,analog,1,");
 	Serial.println(photo);
 	Serial.print("humidity,pc,1,");
 	Serial.println(humid);
 	Serial.print("temperature,C,1,");
 	Serial.println(temp);
}

