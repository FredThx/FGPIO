/*
 * Code pour lecture sonde temprérature DALLAS DS18x et l'envoi en WIFI
 * Materiel associe : Atmega 328  + ESP8266 + DS1820
 * Auteur : FredThx
 *
*/

// Pour sonde dallas
#include <OneWire.h>
#include <DallasTemperature.h>

//Liaison Série au module ESP8266 sur pin 2 et 3
#include <SoftwareSerial.h>

SoftwareSerial ESP8266(2, 3);

// WIFI
String NomduReseauWifi = "WIFI_THOME3"; //TODO : on pourra aussi rechercher le plus fort.
String MotDePasse      = "plus33324333562";

//Serveur web
String host = "192.168.10.10";
int port = 80;
String chaine_send_data = "GET /tempeDB/index.php?table=mesures&capteur=test&temperature=%valeur%"; //%valeur% sera remplace par la valeur

// Echantillonnage
int temps_entre_deux_mesures = 60; // en secondes

//La sonde de température DS18B20 est branchée au pin 10 de l'atmega
OneWire oneWire(10);
DallasTemperature sensors(&oneWire);


//Fonction lancee a l'initialisation du programme
void setup(void)
{
  //On definis les logs a 9600 bauds
  Serial.begin(9600);
  //On initialise le capteur de temperature
  sensors.begin();
  // Une premiere mesure qui deconne toujours
  sensors.requestTemperatures();
  //Liaison série au module WIFI
  ESP8266.begin(115200); 
  initESP8266(); 
}

//Fonction qui boucle a l'infinis
void loop(void)
{ 
  float valeur;
  // Recuperation mesure temperature
  sensors.requestTemperatures();
  valeur = sensors.getTempCByIndex(0);
  // Affichage temperature dans log
  Serial.print("Mesure : ");
  Serial.println(valeur);
  // Envoie la temperature via wifi
  senddatas(valeur);
  // Attente
  attente(temps_entre_deux_mesures);
}

// Fonction qui envoie les données par wifi
void senddatas(float valeur){
  bool resultat;
  String cmd;
    if (valeur > 0){
      Serial.print("Valeur envoyee : ");
      Serial.println(valeur);
      cmd = chaine_send_data;
      cmd.replace("%valeur%", String(valeur));
      resultat = ESP8266_http_request( host, port, cmd);
   }
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
  envoieAuESP8266("AT+CIOBAUD=115200");
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
