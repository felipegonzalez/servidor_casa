//caja_cocina_puerta.ino

int pin_xbee_luz = 3;
int pin_xbee_zumba = 2;
int pin_luz =10;
int pin_zumba=9;
int pin_boton = 7;
int actual_luz = LOW;
int actual_zumba = LOW;

void setup() {
   Serial.begin(9600);
  // put your setup code here, to run once:
  pinMode(pin_xbee_luz, INPUT);
  pinMode(pin_xbee_zumba, INPUT);
  pinMode(pin_boton, INPUT);
  pinMode(pin_luz, OUTPUT);
  pinMode(pin_zumba, OUTPUT);
  digitalWrite(pin_luz, LOW);
  digitalWrite(pin_zumba, LOW);

}

void loop() {
	int read_luz = digitalRead(pin_xbee_luz);
	int read_zumba = digitalRead(pin_xbee_zumba);
	int read_boton = digitalRead(pin_boton);
	//Serial.print(read_luz);
	//Serial.print(" ");
	//Serial.print(read_zumba);
	//Serial.print(" ");
	//Serial.print(read_boton);
	//Serial.print(" ");
	//Serial.println("----------");
	delay(50);
	if(read_luz == 1){
		//digitalWrite(pin_luz, read_luz);
		digitalWrite(pin_luz, HIGH);
	//}
	} else {
		digitalWrite(pin_luz, LOW);
	}

	if(read_zumba == 1){
		digitalWrite(pin_zumba, HIGH);
		delay(3000);
		digitalWrite(pin_zumba, LOW);
	}
	if(read_boton == 1) {
		digitalWrite(pin_zumba, HIGH);
		delay(500); 
		digitalWrite(pin_zumba, LOW);
	}


}
