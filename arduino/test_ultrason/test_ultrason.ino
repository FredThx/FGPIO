
int pin_echo=4;
int pin_trig=3;

  
void setup() {
  Serial.begin(9600);
  pinMode(pin_trig, OUTPUT);
  pinMode(pin_echo, INPUT);
  digitalWrite(pin_trig, LOW);
  delay(200);
}

void loop() {
  Serial.print(distance());
  Serial.println(" cm");
  delay(500);
}

long distance(){
  long duration;
  digitalWrite(pin_trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(pin_trig, LOW);
  duration = pulseIn(pin_echo, HIGH)+10;
  return (duration/2) / 29.1;  
}
