/*
 * Code pour construction d'une sonde de niveau de cuve de fuel "maison", r�cup�re une distance et l'envois sur la fr�quence de 433 mhz
 * Fr�quence : 433.92 mhz
 * Protocole : Ridle (Radio Idle, protocole customis� bas� sur home easy)
 * Licence : CC -by -sa
 * Mat�riel associ� : Atmega 328  + emetteur RF AM 433.92 mhz + capteur UltraSon HC - SR04  + leds de niveau de cuve
 * Auteur : FredThx
 *    Inspiré de Valentin CARRUESCO  aka idleman (idleman@idleman.fr - http://blog.idleman.fr)
 *
 ***Les pins 5, 6, 7, 8 servent � coder la sonde (0V = 1)
 ***	_________
 ***   	|5|6|7|8| 
 ***	|0|0|0|0| Sonde n�0
 ***	|0|0|1|0| Sonde n� 2 (la pin 7 est pont�e avec 0V)
 ***
 */

//Le capteur Ultra son est branché sur les pins suivantes :
const int HRLV_pin=A0;
const float HRLV_scale = 0.5; // 0.5 cm par Vcc/1024 volt

// Pour mesure distance on réalise plusieurs mesures :
const int  nb_loop_for_safe_distance = 8;
const int nb_essais_avant_nosubmit = 50;
const float precision = 2.5;
const int nb_mesures = 8;

// Des leds pour voir le niveau de la cuve en local
int pin_led[5] = {9,10,11,12,13};
int niveaux[5] = {140, 105,70,35};

//L'émetteur radio 433 mhz est branché au pin 9 de l'atmega
#define TRANSMITTER_PIN 2 //9

//Codage de la sonde (sera utilisée pour l'identifier sur le "réseau" 433 Mhz
int CODE_PIN[4]={5,6,7,8};

//Tableaud de stockage du signal binaire a envoyer
bool bit2[26]={};

//variables globales pour mesures
long validate_distance = 0;
int nb_mesures_realisees = 0;
long mesures[10];
int essais = 0;
bool alerte = false;

//Fonction lancee a l'initialisation du programme
void setup(void)
{
  //On definis les logs � 9600 bauds
  Serial.begin(9600);
  // On initialise le mode des leds
  for (int i=0;i<5;i++) {
	pinMode(pin_led[i], OUTPUT);
  }
  //On d�finis le pin reli� � l'emetteur en tant que sortie
  pinMode(TRANSMITTER_PIN, OUTPUT);  
  //On d�finis les pins pour le codage en tant que entree
  for (int i=0;i<4;i++) {
	pinMode(CODE_PIN[i], INPUT_PULLUP);
  }
}

//Fonction qui boucle a l'infinis
void loop(void)
{ 
  if ((validate_distance == 0) and (essais <= nb_essais_avant_nosubmit)){
    //Pour faire patienter lors du démarrage
    allume_one_led(nb_mesures_realisees);
  }
  long distance = 0;
  if (nb_mesures_realisees < nb_mesures){
    distance = safe_distanceUltraSonic(precision); //x de précision demandée. Sinon distance = 0
    essais +=1;
    if (distance > 0){
        essais = 0;
        mesures[nb_mesures_realisees] = distance;
        nb_mesures_realisees +=1;
        //Affichage de la temperature dans les logs
        Serial.print("Mesure no ");
        Serial.print(nb_mesures_realisees);
        Serial.print(" : Distance : ");
        Serial.print(distance);
        Serial.println(" cm");
        senddatas(validate_distance);
    }
    else{
      //S'il y a trop de mauvaise lectures, on ne renvoie pas la distance et on met les leds en mode erreur
      if (essais > nb_essais_avant_nosubmit){
            digitalWrite(pin_led[0], HIGH);// led rouge
            delay(500);
            digitalWrite(pin_led[0], LOW);// led rouge
            delay(500);
            if (alerte){
                digitalWrite(pin_led[0], HIGH);// led rouge
            }
          Serial.println("Erreur : mesure impossible");
          maj_leds(999);
          }
       else{
         senddatas(validate_distance);
       }
    }
  }
  else{
    //Si on a mesurer un nombre sufisant de valeurs correctes, on prend la plus grande et on la transmet
    validate_distance = maximum(mesures, nb_mesures);
    senddatas(validate_distance);
    maj_leds(validate_distance); //Selon les niveaux, on allume les leds
    nb_mesures_realisees = 0;
 }
}

//Fonction pour mise à jours des leds
void maj_leds(long distance){
    //On etteint tout pour faire clignoter un peu
    for (int i=0;i<5;i++){
      digitalWrite(pin_led[i], LOW);// leds vertes
    }
    delay(100);
    if (distance > niveaux[0]){
          digitalWrite(pin_led[0], HIGH);// led rouge
          alerte = true;
    }
    else{
          alerte = false;
    }
    for (int i=1;i<5;i++){
          if (distance < niveaux[i-1]){
              digitalWrite(pin_led[i], HIGH);// leds vertes
          }
    }
}

//Fonction pour allumer une seule led verte (pas pin_led[0])
void allume_one_led(int no_led){
  //On etteint la led prededente
  digitalWrite(pin_led[1 + (no_led-1) % 4], LOW);
  //On allume la suivante
  digitalWrite(pin_led[1 + no_led % 4], HIGH);  
}
// Fonction qui envoie les données par radio

void senddatas(long distance){
    if (distance > 0){
      Serial.print("                                        Distance envoyee : ");
      Serial.println(distance);
      //Conversion de la temperature en binaire et stockage sur 10 bits dans le tableau bit2
        itob(distance,10); 
        //Envois du signal radio comprenant la temperature (on l'envois 5 fois pour être bien sur du coup)
        int i=0;
        for(i=0; i<5;i++){
            transmit();
            delayMicroseconds(666);   
        }
      delay(3000);
   }
}

//Fonction de tansmission radio
void transmit()
{
 
  // On envois 2 impulsions 1->0 avec un certain delais afin de signaler le d�part du siganl( verrou de d�part)
  //Initialisation radio � 1
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
 
 //On envois les 11 bits stock�s dans le tableau bit2
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
 
//Fonction d'envois d'un bit cod� en manchester (0 = 01 et 1 = 10) 
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
 
//fonction de conversion d'un nombre d�cimal "integer" en binaire sur "length" bits et stockage dans le tableau bit2
void itob(unsigned long integer, int length)
{  
  int positive;
  if(integer>0){
   positive = true;
   //Serial.println("positif ");
 }else{
  positive = false;
   //Serial.println("negatif ");
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
 //D�finit le signe (+ ou -)
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
float distanceUltraSonic(){
  return analogRead(HRLV_pin)*HRLV_scale;  
}

int safe_distanceUltraSonic(float precision){
	float distances[nb_loop_for_safe_distance];
	for (int i=0;i<nb_loop_for_safe_distance;i++){
		distances[i] = distanceUltraSonic();
		delay(100);
	}
	if (3*ecartype(distances) < precision){
		return arrondi(moyenne(distances));
	}
	else{
		return 0;
	}
}

float moyenne(float valeurs[]){
	float somme = 0;
	for (int i=0;i<nb_loop_for_safe_distance;i++){
		somme += valeurs[i];
	}
	return somme / nb_loop_for_safe_distance;
}

float ecartype(float valeurs[]){
	float moy = moyenne(valeurs);
	float variance=0;
	for (int i=0;i<nb_loop_for_safe_distance;i++){
		variance += pow((valeurs[i]-moy),2);
	}
	Serial.print("moyenne : ");
	Serial.print(moy);
	Serial.print(" / 3 * Ecartype : ");
	Serial.println(3*pow(variance, 0.5));

	return pow(variance, 0.5);
}

long arrondi(float val){
  return (long)(val+0.5);
 }
 
long maximum(long tableau[], int taille){
  int max = 0;
  Serial.println("Calcul du maximum");
  for (int i=0;i<taille;i++){
    Serial.println(tableau[i]);
    if(tableau[i]>max){
      max=tableau[i];
    }
  }
  Serial.print("Max : ");
  Serial.println(max);
  return max;
}
