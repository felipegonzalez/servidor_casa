//prueba_ac.ino

int led = 13;
int no_samples = 100;
int samples[100];

void setup() {
  // put your setup code here, to run once:
  pinMode(led, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
    digitalWrite(led, HIGH);  // turn the LED on (HIGH is the voltage level)  
              // wait for a second
    
    float suma = 0;
    for(int i = 0; i < no_samples; i++) {
    	int val = analogRead(0);
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
    Serial.println(rms);
    Serial.println("---");
    delay(1000);
}
