/*
 * Code pour construction d'une sonde de niveau de cuve de fuel "maison", r�cup�re une distance et l'envois en WIFI
 * Mat�riel associ� : Atmega 328  + emetteur RF AM 433.92 mhz + capteur UltraSon HC - SR04  + leds de niveau de cuve
 * Auteur : FredThx
 *
*/

//Liaison Série au module ESP8266 sur pin 6 et 7
#include <SoftwareSerial.h>
SoftwareSerial ESP8266(10, 11);

// WIFI
const String NomduReseauWifi = "WIFI_THOME1"; //TODO : on pourra aussi rechercher le plus fort.
const String MotDePasse      = "plus33324333562";

//Serveur web
const String host = "192.168.10.10";
const int port = 80;
const String chaine_send_data = "GET /tempeDB/index.php?table=mesures&capteur=CuveFuel&temperature=%distance%"; //%distance% sera remplace par la valeur

// Echantillonnage
const int temps_entre_deux_mesures = 60; // en secondes

//Le capteur Ultra son est branché sur les pins suivantes :
const int HRLV_pin=A0;
const float HRLV_scale = 0.5; // 0.5 cm par Vcc/1024 volt

// Pour mesure distance on réalise plusieurs mesures :
const int  nb_loop_for_safe_distance = 8;
const int nb_essais_avant_nosubmit = 50;
const float precision = 2.5;
const int nb_mesures = 8;

// Des leds pour voir le niveau de la cuve en local
int pin_led[5] = {3,4,5,6,7};
int niveaux[5] = {140, 105,70,35};

//variables globales pour mesures
long validate_distance = 0;
int nb_mesures_realisees = 0;
long mesures[10];
int essais = 0;
bool alerte = false;

//Fonction lancee a l'initialisation du programme
void setup(void)
{
  //On definis les logs a 9600 bauds
  Serial.begin(9600);
  //Liaison série au module WIFI
  ESP8266.begin(9600); 
  initESP8266();
  
  // On initialise le mode des leds
  for (int i=0;i<5;i++) {
	pinMode(pin_led[i], OUTPUT);
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
        //Affichage de la mesure dans les logs
        Serial.print("Mesure no ");
        Serial.print(nb_mesures_realisees);
        Serial.print(" : Distance : ");
        Serial.print(distance);
        Serial.println(" cm");
        //senddatas(validate_distance);
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
         //senddatas(validate_distance);
       }
    }
  }
  else{
    //Si on a mesurer un nombre sufisant de valeurs correctes, on prend la plus grande et on la transmet
    validate_distance = maximum(mesures, nb_mesures);
    senddatas(validate_distance);
    maj_leds(validate_distance); //Selon les niveaux, on allume les leds
    nb_mesures_realisees = 0;
    attente(temps_entre_deux_mesures);
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

// Fonction qui envoie les données par wifi
void senddatas(long distance){
  bool resultat;
  String cmd;
    if (distance > 0){
      Serial.print("                                        Distance envoyee : ");
      Serial.println(distance);
      cmd = chaine_send_data;
      cmd.replace("%distance%", String(distance));
      resultat = ESP8266_http_request( host, port, cmd);
   }
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

/****************************************************************/
/*                Fonction qui initialise l'ESP8266             */
/****************************************************************/
void initESP8266()
{  
  Serial.println("**********************************************************");  
  Serial.println("**************** DEBUT DE L'INITIALISATION ***************");
  Serial.println("**********************************************************");  
  envoieAuESP8266("AT+RST");
  recoitDuESP8266(2000);
  Serial.println("**********************************************************");  
  envoieAuESP8266("AT+CIOBAUD=9600");
  recoitDuESP8266(2000);
  Serial.println("**********************************************************");
  envoieAuESP8266("AT+CWMODE=1");
  recoitDuESP8266(5000);
  Serial.println("**********************************************************");
  envoieAuESP8266("AT+CWJAP=\""+ NomduReseauWifi + "\",\"" + MotDePasse +"\"");
  recoitDuESP8266(10000);
  Serial.println("**********************************************************");
  envoieAuESP8266("AT+CIFSR");
  recoitDuESP8266(1000);
  Serial.println("**********************************************************");
  envoieAuESP8266("AT+CIPMUX=0");   
  recoitDuESP8266(1000);
  Serial.println("**********************************************************");
//  envoieAuESP8266("AT+CIPSTART=\"TCP\",\"184.106.153.149\",80");   
  recoitDuESP8266(1000);
  String cmd = "AT+CIPSTART=\"TCP\",\""+host+"\","+port;
  envoieAuESP8266(cmd);
  recoitDuESP8266(1000);
  Serial.println("**********************************************************");
  Serial.println("***************** INITIALISATION TERMINEE ****************");
  Serial.println("**********************************************************");
  Serial.println("");  
}

/****************************************************************/
/*        Fonction qui envoie une commande à l'ESP8266          */
/****************************************************************/
void envoieAuESP8266(String commande)
{  
  Serial.println("send cmd : " + commande);
  ESP8266.println(commande);
}
/****************************************************************/
/*Fonction qui lit et affiche les messages envoyés par l'ESP8266*/
/****************************************************************/
String recoitDuESP8266(const int timeout)
{
  String reponse = "";
  long int time = millis();
  while( (time+timeout) > millis())
  {
    while(ESP8266.available())
    {
      char c = ESP8266.read();
      reponse+=c;
    }
  }
  Serial.println(reponse);
  return reponse;
}
/****************************************************************/
/*Fonction qui envoie une requete http a un serveur*/
/* exemple : ESP8266_http_request("184.106.153.149",80,"GET /update?key=PJS26TIGV9EKVYE1&field1=21")
/****************************************************************/
bool ESP8266_http_request(String host, int port, String http_cmd)
{
  Serial.println("Requete http : " + http_cmd);
  String commande;
  String reponse;
   
  commande = "AT+CIPSTART=\"TCP\",\"" + host + "\"," + port;
  envoieAuESP8266(commande);
  recoitDuESP8266(2000);
   
  commande = "AT+CIPSEND=" + String(http_cmd.length()+2);
  Serial.println("===>" + commande + "-----");
  envoieAuESP8266(commande);
  recoitDuESP8266(2000);
  
  envoieAuESP8266(http_cmd);
  reponse = recoitDuESP8266(2000);
  //TODO : analyse de la reponse du serveur
  
  return true;
}

void attente(int secondes){
  Serial.print("Attente");
  for(int i=0;i<secondes;i++){
    Serial.print(".");
    delay(1000);
  }
  Serial.println("ok"); 
}
