#define pin_pir 12
#define pin_photo 1
#define pin_irled 13
#define pin_ac 0

int motion;
int photo;
long tiempo_actual;
long tiempo_ultima;
long tiempo_pir;
int no_samples = 100;
int samples[100];

void setup()  {                
  pinMode(pin_irled, OUTPUT);
  pinMode(pin_pir, INPUT);      
  Serial.begin(9600);
  tiempo_ultima = millis();
  tiempo_actual = millis();
}

void loop() {
  motion = digitalRead(pin_pir);
  tiempo_actual = millis();

  if(tiempo_actual >= tiempo_ultima + 20000){
    registrar_enviar();
    tiempo_ultima = millis();
  }
  if(motion==0){
    if(tiempo_actual >= tiempo_pir + 2000){
      tiempo_pir = millis();
      tiempo_ultima = millis();
      registrar_enviar();
    }
  }

	if(Serial.available() > 0){
      char leer = Serial.read();
      if(leer=='1') {
        SendOnCode();
      }
  }
}



void pulseIR(long microsecs) {
  // we'll count down from the number of microseconds we are told to wait
 
  cli();  // this turns off any background interrupts
 
  while (microsecs > 0) {
    // 38 kHz is about 13 microseconds high and 13 microseconds low
   digitalWrite(pin_irled, HIGH);  // this takes about 3 microseconds to happen
   delayMicroseconds(9);         // hang out for 10 microseconds, you can also change this to 9 if its not working
   digitalWrite(pin_irled, LOW);   // this also takes about 3 microseconds
   delayMicroseconds(9);         // hang out for 10 microseconds, you can also change this to 9 if its not working
 
   // so 26 microseconds altogether
   microsecs -= 24;
  }
 
  sei();  // this turns them back on
}
 
void SendOnCode() {
  // This is the code for my particular Nikon, for others use the tutorial
  // to 'grab' the proper code from the remote
 int IRsignal[] = {
// ON, OFF (in 10's of microseconds)
 890, 442,
58, 162,
58, 164,
58, 52,
58, 52,
58, 54,
56, 54,
58, 52,
58, 162,
58, 52,
60, 162,
58, 162,
58, 54,
58, 52,
58, 52,
58, 52,
58, 54,
58, 162,
58, 52,
58, 164,
56, 54,
58, 52,
58, 52,
58, 52,
60, 52,
58, 52,
58, 164,
58, 52,
56, 54,
58, 162,
60, 162,
58, 52,
58, 54,
56, 54,
58, 52,
58, 52,
58, 52,
58, 52,
58, 54,
58, 52,
56, 54,
58, 54,
56, 54,
58, 52,
58, 52,
58, 52,
60, 50,
60, 52,
58, 52,
58, 786,
58, 52,
58, 52,
58, 52,
60, 52,
56, 54,
58, 52,
58, 52,
58, 54,
58, 52,
58, 52,
58, 52,
58, 52,
58, 54,
56, 54,
58, 52,
58, 52,
58, 52,
60, 52,
58, 52,
58, 52,
58, 52,
58, 54,
58, 52,
56, 54,
58, 52,
58, 52,
58, 54,
58, 52,
58, 52,
58, 52,
58, 54,
58, 52,
58, 52,
58, 52,
58, 52,
58, 54,
58, 52,
58, 52,
58, 52,
58, 54,
56, 54,
58, 52,
58, 52,
58, 52,
60, 50,
58, 54,
58, 52,
58, 52,
58, 54,
56, 54,
58, 52,
58, 52,
58, 52,
60, 50,
60, 52,
58, 58,
58, 162,
58, 162,
58, 164,
58, 52,
58, 164,
58, 162,
58, 52,
58, 52,
58, 0};

  for(int i=0; i < 230; i+= 2){
    //Serial.println(i);
    pulseIR(IRsignal[i]*10);
    //Serial.println(i);
    delayMicroseconds(IRsignal[i+1]*10);
  }
 }

 void registrar_enviar() {
  motion = digitalRead(pin_pir);
  photo = analogRead(pin_photo);
  Serial.print("pir,binary,1,");
  Serial.println(1-motion);
  Serial.print("photo,analog,1,");
  Serial.println(photo);
  float suma = 0;
  for(int i = 0; i < no_samples; i++) {
      int val = analogRead(pin_ac);
      samples[i] = val;
      suma = suma + val;
      delay(2);
    }
  float media = suma/no_samples;
  float suma_cuad = 0;
  for(int i =0; i < no_samples; i++){
      suma_cuad = suma_cuad + (samples[i] - media)*(samples[i] -  media);
  }
  float rms = sqrt(suma_cuad/no_samples);
  Serial.print("ac_current,rms,1,");
  Serial.println(rms);
}
