/*
 * Code pour construction d'une sonde de niveau de cuve de fuel "maison", r?cup?re une distance et l'envois sur la fr?quence de 433 mhz
 * Fr?quence : 433.92 mhz
 * Protocole : Ridle (Radio Idle, protocole customis? bas? sur home easy)
 * Licence : CC -by -sa
 * Mat?riel associ? : Atmega 328  + emetteur RF AM 433.92 mhz + capteur UltraSon HC - SR04  + leds de niveau de cuve
 * Auteur : FredThx
 *    Inspiré de Valentin CARRUESCO  aka idleman (idleman@idleman.fr - http://blog.idleman.fr)
 *
 ***Les pins 5, 6, 7, 8 servent ? coder la sonde (0V = 1)
 ***	_________
 ***   	|5|6|7|8| 
 ***	|0|0|0|0| Sonde n?0
 ***	|0|0|1|0| Sonde n? 2 (la pin 7 est pont?e avec 0V)
 ***
 */

//Le capteur Ultra son est branché sur les pins suivantes :
int pin_echo=4;
int pin_trig=3;
// Des leds pour voir le niveau de la cuve en local
int pin_led[5] = {9,10,11,12,13};
int niveaux[5] = {140, 105,70,35};

//L'émetteur radio 433 mhz est branché au pin 9 de l'atmega
#define TRANSMITTER_PIN 2 //9

//Codage de la sonde (sera utilisée pour l'identifier sur le "réseau" 433 Mhz
int CODE_PIN[4]={5,6,7,8};

//Tableau de stockage du signal binaire ? envoyer
bool bit2[26]={};              


//Fonction lanc?e ? l'initialisation du programme
void setup(void)
{
  //On definis les logs ? 9600 bauds
  Serial.begin(9600);
  //On initialise le capteur UltraSon
  pinMode(pin_trig, OUTPUT);
  pinMode(pin_echo, INPUT);
  digitalWrite(pin_trig, LOW);
  delay(200);
  // On initialise le mode des leds
  for (int i=0;i<5;i++) {
	pinMode(pin_led[i], OUTPUT);
  }
  //On d?finis le pin reli? ? l'emetteur en tant que sortie
  pinMode(TRANSMITTER_PIN, OUTPUT);  
  //On d?finis les pins pour le codage en tant que entree
  for (int i=0;i<4;i++) {
	pinMode(CODE_PIN[i], INPUT_PULLUP);
  }
}

//Fonction qui boucle ? l'infinis
void loop(void)
{ 
  long distance;
  //Lancement de la commande de r?cuperation de la temperature
  distance = distanceUltraSonic();
  //Affichage de la temperature dans les logs
  Serial.print("Distance : ");
  Serial.print(distance);
  Serial.println(" cm");
  //Conversion de la temperature en binaire et stockage sur 10 bits dans le tableau bit2
  itob(distance,10); 
  //Envois du signal radio comprenant la temperature (on l'envois 5 fois parce qu'on est pas des trompettes :p, et on veux ?tre s?r que ?a recoit bien)
  int i=0;
  for(i=0; i<5;i++)
  {
    transmit();
    delayMicroseconds(666);   
  }
  //Selon les niveaux, on allume les leds
  if (distance > niveaux[0]){
     digitalWrite(pin_led[0], HIGH);
  }
  else{
     digitalWrite(pin_led[0], LOW);
  }
  for (i=1;i<5;i++){
    if (distance < niveaux[i-1]){
      digitalWrite(pin_led[i], HIGH);
    }
    else{
      digitalWrite(pin_led[i], LOW);
    }
   }
    
  //delais de 5sc avant le prochain envois
  delay(5000);
  
}

//Fonction de tansmission radio
void transmit()
{
 
  // On envois 2 impulsions 1->0 avec un certain delais afin de signaler le d?part du siganl( verrou de d?part)
  //Initialisation radio ? 1
  digitalWrite(TRANSMITTER_PIN, HIGH);
  delayMicroseconds(275);     
  //Verrou 1
  digitalWrite(TRANSMITTER_PIN, LOW);
  delayMicroseconds(9900);     
  digitalWrite(TRANSMITTER_PIN, HIGH); 
  //Pause entre les verrous  
  delayMicroseconds(275);     
  //Verrou 2
  digitalWrite(TRANSMITTER_PIN, LOW);    
  delayMicroseconds(2675);
  // End on a high
  digitalWrite(TRANSMITTER_PIN, HIGH);
 
 //On envois les 11 bits stock?s dans le tableau bit2
 int i;
 for(i=0; i<11;i++)
 {
    sendPair(bit2[i]);
 }
 
 //On envois le code de la sonde (1010 = code 10)
  for (int i=0;i<4;i++) {
        sendPair(digitalRead(CODE_PIN[i])== LOW);
  }
 
 //On envois un verrou de fin pour signaler la fin du signal :)
  digitalWrite(TRANSMITTER_PIN, HIGH);   
  delayMicroseconds(275);     
  digitalWrite(TRANSMITTER_PIN, LOW);  
 
}
 
//Fonction d'envois d'un bit pure (0 ou 1) 
void sendBit(boolean b) {
  if (b) {
    digitalWrite(TRANSMITTER_PIN, HIGH);
    delayMicroseconds(310);   //275 orinally, but tweaked.
    digitalWrite(TRANSMITTER_PIN, LOW);
    delayMicroseconds(2500);  //1225 orinally, but tweaked.
  }
  else {
    digitalWrite(TRANSMITTER_PIN, HIGH);
    delayMicroseconds(310);   //275 orinally, but tweaked.
    digitalWrite(TRANSMITTER_PIN, LOW);
    delayMicroseconds(1000);   //275 orinally, but tweaked.
  }
}
 
//Fonction d'envois d'un bit cod? en manchester (0 = 01 et 1 = 10) 
void sendPair(boolean b) {
  if(b)
  {
    sendBit(true);
    sendBit(false);
  }
  else
  {
  sendBit(false);
  sendBit(true);
  }
}
 
//fonction de conversion d'un nombre d?cimal "integer" en binaire sur "length" bits et stockage dans le tableau bit2
void itob(unsigned long integer, int length)
{  
  int positive;
  if(integer>0){
   positive = true;
   Serial.println("positif ");
 }else{
  positive = false;
   Serial.println("negatif ");
 }
  //needs bit2[length]
  // Convert long device code into binary (stores in global bit2 array.)
 for (int i=0; i<length; i++){
   if ((integer / power2(length-1-i))==1){
     integer-=power2(length-1-i);
     bit2[i]=1;
   }
   else bit2[i]=0;
 }
 //D?finit le signe (+ ou -)
 if(positive){
   bit2[length]=1;
 }else{
   bit2[length]=0;
 }
}

//Calcule 2^"power"
unsigned long power2(int power){    
 unsigned long integer=1;          
 for (int i=0; i<power; i++){      
   integer*=2;
 }
 return integer;
}

//Mesure la distance avec le capteur UltraSon
long distanceUltraSonic(){
  long duration;
  digitalWrite(pin_trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(pin_trig, LOW);
  duration = pulseIn(pin_echo, HIGH)+10;
  return (duration/2) / 29.1;  
}