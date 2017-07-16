#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
 Gestion du capteur de présence optique QRD1114
	composé d'un émetteur IR (led)
	et d'un recepteur phototransistor
		
	Dans l'absolu, on peut l'utiliser comme capteur de distance (mais la plage de detection
	est comprise entre 0 et 1 cm.
	=> On l'utilise ici comme detecteur de présence, donc comme capteur digital.
	
	Wiring :
						 __
					0V--|  |---[200ohms]--5V
		analog_pin_io --|__|---0V		|
					   |				|
					   |----[10kohms]--|
			
	(-- : petite patte)
	(--- : grande patte)
		
	Quand un objet (pas noir) s'approche, la lumière IR est réfléchie
	et la tension sur la pin de sortie baisse vers 0V
	(pas d'objet : 2.9 volts)
	
	Pour raspberry pi : utilisation d'un module mcp300x pour entrée analogique.
	
	Utilisation avec Thread : bien sur!
	
 AUTEUR : FredThx

 Projet : rpiduino_io

'''
from rpiduino_io import *

class qrd1114_io(device_io):
	'''capteur de présence optique
	'''
	def __init__(self, pin):
		assert isinstance(pin, analog_pin_io), 'pin must be a analog_pin_io'
		self.pin = pin

class qrd1114_digital_io(qrd1114_io, digital_input_device_io):
	''' Capteur de présence optique QRD114 en mode tout ou rien
	'''
	def __init__(self, pin, seuil=1, thread = False, on_changed = None, pause = 0.1):
		'''Initialisation
			- pin		:	a analog_pin_io
		'''
		qrd1114_io.__init__(self, pin)
		self.seuil = seuil
		self.last_state= False
		digital_input_device_io.__init__(self, thread, on_changed, pause)
	
	def read(self):
		return self.pin.get_voltage()<self.seuil
		
	def is_detected(self):
		''' renvoie true si le capteur passe de rien à quelque chose
			(une fois la detection faite, renvoie False, même si l'objet est encore là)
		'''
		value = self.read()
		if self.last_state == value:
			return False
		else:
			self.last_state = value
			return value

class qrd1114_analog_io(qrd1114_io, analog_input_device_io):
	'''Capteur de présence optique QRD114 en mode analogique
	'''
	def __init__(self, pin, seuil = 1, thread = False, on_changed = None, discard = 0.1, pause = 0.1, timeout = 5):
		'''Initialisation
			- pin			:	a analog_pin_io
			- seuil			:	seuil de déclenchement du deamon
								soit un tuple (seuil_bas, seuil_haut)
								soit une seule valeur				
			- thread		:	(facultatif) True si utilisation thread
			- on_changed	:	fonction ou string executable
								qui sera lancée quand la valeur du capteur change
			- discard		:	ecart en dessous duquel une valeur est considérée comme inchangée
			- pause 		:	pause entre chaque lecture du composant
			- timeout		:	durée après laquelle une valeur lue est obsolète
		'''
		qrd1114_io.__init__(self, pin)
		analog_input_device_io.__init__(self, seuil, thread, on_changed, discard, pause, timeout)
		
	def read(self):
		'''Renvoie le voltage mesuré par le capteur
		'''
		return self.pin.get_voltage()
		
		
		
			
			
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	from mcp300x_hspi_io import *
	from led_io import *
	
	pc = rpiduino_io()
	mcp3008 = mcp3008_hspi_io()	#Pour lecture analogique sur Rpi
	led = led_io(pc.bcm_pin(16))
	capteur = qrd1114_digital_io(mcp3008.pin[0])
	compteur = 0
	while True:
		if capteur.is_detected():
			compteur +=1
			led.blink(0.1,0.001,0.1)
			print compteur
