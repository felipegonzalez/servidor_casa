
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

DHT dht(pin_dht, dht_type);

void setup() {
	dht.begin();
	pinMode(pin_pir, INPUT);
	delay(3000);
	Serial.begin(9600);
	myservo.attach(12);


}

void loop() {
	delay(1000);
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
 	if(Serial.available()){
    	char leer = Serial.read();
    	//Serial.println(leer);
    	if(leer=='1'){
      		myservo.write(0);
    	}
    	if(leer=='2'){
      		myservo.write(45);
    	}
    	if(leer=='3'){
      		myservo.write(90);
    	}
    	if(leer=='4'){
      		myservo.write(135);
    	}
    	if(leer=='5'){
      		myservo.write(179);
    	}
  }
}

