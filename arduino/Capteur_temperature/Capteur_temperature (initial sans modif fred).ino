/*
 * Code pour construction d'une sonde de temperature "maison", récupère une temperature et l'envois sur la fréquence de 433 mhz
 * Fréquence : 433.92 mhz
 * Protocole : Ridle (Radio Idle, protocole customisé basé sur home easy)
 * Licence : CC -by -sa
 * Matériel associé : Atmega 328 (+résonateur associé) + emetteur RF AM 433.92 mhz + capteur DS18B20 + led d'etat + résistance 4.7 kohms
 * Auteur : Valentin CARRUESCO  aka idleman (idleman@idleman.fr - http://blog.idleman.fr)
 */
 
#include <OneWire.h>
#include <DallasTemperature.h>

//La sonde de température DS18B20 est branchée au pin 10 de l'atmega
#define TEMPERATURE_PIN 10
//L'émetteur radio 433 mhz est branché au pin 9 de l'atmega
#define TRANSMITTER_PIN 9

//Tableau de stockage du signal binaire à envoyer
bool bit2[26]={};              


// On crée une instance de la classe oneWire pour communiquer avec le materiel on wire (dont le capteur ds18b20)
OneWire oneWire(TEMPERATURE_PIN);
//On passe la reference onewire à la classe DallasTemperature qui vas nous permettre de relever la temperature simplement
DallasTemperature sensors(&oneWire);

//Fonction lancée à l'initialisation du programme
void setup(void)
{
  //On definis les logs à 9600 bauds
  Serial.begin(9600);
  //On initialise le capteur de temperature
  sensors.begin();
  //On définis le pin relié à l'emetteur en tant que sortie
  pinMode(TRANSMITTER_PIN, OUTPUT);   
}

//Fonction qui boucle à l'infinis
void loop(void)
{ 

  //Lancement de la commande de récuperation de la temperature
  sensors.requestTemperatures();
  //Affichage de la temparature dans les logs
  Serial.println(sensors.getTempCByIndex(0));  
  //Conversion de la temperature en binaire et stockage sur 7 bits dans le tableau bit2
  itob(sensors.getTempCByIndex(0),7); 
  //Envois du signal radio comprenant la temperature (on l'envois 5 fois parce qu'on est pas des trompettes :p, et on veux être sûr que ça recoit bien)
  int i=0;
  for(i=0; i<5;i++)
  {
    transmit();
    delayMicroseconds(666);   
  }
  //delais de 5sc avant le prochain envois
  delay(5000);
}

//Fonction de tansmission radio
void transmit()
{
 
  // On envois 2 impulsions 1->0 avec un certain delais afin de signaler le départ du siganl( verrou de départ)
  //Initialisation radio à 1
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
 
 //On envois les 8 bits stockés dans le tableau bit2
 int i;
 for(i=0; i<8;i++)
 {
    sendPair(bit2[i]);
 }
 
 //On envois le code de la sonde (1010 = code 10)
 sendPair(true);
 sendPair(false);
 sendPair(true);
 sendPair(false);
 
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
 
//Fonction d'envois d'un bit codé en manchester (0 = 01 et 1 = 10) 
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
 
//fonction de conversion d'un nombre décimal "integer" en binaire sur "length" bits et stockage dans le tableau bit2
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
 //Définit le signe (+ ou -)
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
