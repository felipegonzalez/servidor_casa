// caja_3.ino
#define pin_pir 4
#define pin_photo 1
#define pin_reed 12
#define pin_piezo 11
#define pin_tmp 0
int photo;
int motion;
int door;


void setup() {
	pinMode(pin_pir, INPUT);
	pinMode(pin_reed, INPUT);
	delay(5000);
	Serial.begin(9600);
}


void loop() {
	delay(1000);
	int reading = analogRead(pin_tmp);  
 
 	// converting that reading to voltage, for 3.3v arduino use 3.3
 	float voltage = reading * 5.0;
 	voltage /= 1024.0; 
	motion = digitalRead(pin_pir);
	photo = analogRead(pin_photo);
	door  = digitalRead(pin_reed);
 	//Serial.println("Lecturas: ");
 	Serial.print("pir,binary,1,");
 	Serial.println(motion);
 	Serial.print("photo,analog,1,");
 	Serial.println(photo);
 	Serial.print("reed,binary,1,");
 	Serial.println(door);

}


