// caja_3.ino
#define pin_pir 4
#define pin_photo 1
#define pin_reed 12
#define pin_tmp 0
int photo;
int motion;
int door;
int door_anterior;
long tiempo_actual;
long tiempo_ultima;
long tiempo_pir;


void setup() {
	pinMode(pin_pir, INPUT);
	pinMode(pin_reed, INPUT);
	delay(5000);
	Serial.begin(9600);
	door_anterior = digitalRead(pin_reed);
	tiempo_ultima = millis();
    tiempo_actual = millis();
    tiempo_pir = millis();
}


void loop() {
	motion = digitalRead(pin_pir);
	door  = digitalRead(pin_reed);
	tiempo_actual = millis();

	if(motion==1){
    	if(tiempo_actual >= tiempo_pir + 2000){
      		tiempo_pir = millis();
      		tiempo_ultima = millis();
      		registrar_enviar();
    	}
  	}

  	if(door_anterior!=door){
  			door_anterior = digitalRead(pin_reed);
  		    tiempo_ultima = millis();
      		registrar_enviar();
  	}

	if(tiempo_actual >= tiempo_ultima + 20000){
    	registrar_enviar();
    tiempo_ultima = millis();
  }
	//delay(1000);
	
}

void registrar_enviar(){
	int reading = analogRead(pin_tmp);  
 	float voltage = reading * 5.0;
 	voltage /= 1024.0; 
 	float temperatureC = (voltage - 0.5) * 100 ;  
	motion = digitalRead(pin_pir);
	photo = analogRead(pin_photo);
	door  = digitalRead(pin_reed);
 	//Serial.println("Lecturas: ");
 	Serial.print("pir,binary,1,");
 	Serial.println(motion);
 	Serial.print("photo,analog,1,");
 	Serial.println(photo);
 	Serial.print("puerta,binary,1,");
 	Serial.println(door);
 	Serial.print("temperature,C,1,");
 	Serial.println(temperatureC);
}

