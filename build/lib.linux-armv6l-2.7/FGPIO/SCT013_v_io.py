#!/usr/bin/python
# -*- coding:utf-8 -*

"""
 Classe 
	Module SCT013 de YHDC
	(ie tore)
	pour mesure puissance dans circuit electrique
	en mode sortie 0-1Volt
	(ne fonctionne pas avec 100A/33mA)
	
	
	Wiring :
	
		 ________
		|  ____  |
		| |    | |
		| |    | |______________________ digital_pin (via MPC3008 for Rpi)
		| |    | |______________________ 0V
		| |____| |
		|________|  
	
	sur un rpiduino_io
		- Rpi
		- pcduino

 AUTEUR : FredThx

 Projet : rpiduino_io

"""

from device_io import *
from pin_io import *
import math
import time
import logging


class SCT013_v_io (analog_input_device_io):
	'''Module SCT03
	'''
	nb_cycles_mesure = 2
	
	def __init__(self, input_pin, Imax = 30.0, Vmax = 1.0, V0 = 240.0, freq = 50.0, seuil = 50, thread = False, on_changed = None, discard = 10, pause = 0.1, timeout = 5):
		'''Initialisation
				- input_pin		:	a analog_pin_io
				- Imax			:	Maximum intensity of the sensor
				- Vmax			:	voltage for Imax
				- freq			:	frequency of the electric curent
				
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
		assert isinstance(input_pin, analog_pin_io), "input_pin must be a analog_pin_io"
		self.input_pin = input_pin
		self.Imax = float(Imax)
		assert Vmax!=0, "Vmax cannot be zéro."
		self.Vmax = float(Vmax)
		self.V0 = float(V0)
		assert freq!=0, "freq cannot be zéro."
		self.freq = float(freq)
		analog_input_device_io.__init__(self, seuil, thread, on_changed, discard, pause, timeout)
		logging.info('SCT013_v_io create on %s' % self.input_pin)

	def read(self):
		'''return the measured instantaneous power in Watts
		'''
		maxi = 0
		fin = time.time() + self.nb_cycles_mesure/self.freq
		while time.time() < fin:
			maxi = max(maxi, self.input_pin.get_voltage())
		voltage = maxi / math.sqrt(2)
		return self.V0 * self.Imax / self.Vmax * voltage 



#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	from mcp300x_hspi_io import *
	
	# Utilisation sur Rpi d'un module pour entrées analogique
	# Pour pcduino :
	#	pc = rpiduino()
	#	ch0 = pc.pin['A0']
	
	mcp3008 = mcp3008_hspi_io()
	ch0 = mcp3008.pin[0]
	circuit = SCT013_v_io(ch0)
	try:
		while True:
			print "Puissance mesurée : %.0f" % circuit.read()
			time.sleep(1)
	except KeyboardInterrupt:
		pass
	
	#Utilisation des thread
	def alerte():
		if circuit.high():
			print "Puissance du circuit trop élevée : %s" % circuit.th_readed()
		
	circuit = SCT013_v_io(ch0, seuil = 500, thread = True, on_changed = alerte)
	
	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			# Lecture en continue du capteur, pendant ce temps, le thread agit
			print "Puissance mesurée : %s" % circuit.th_readed()
			time.sleep(1)
	except KeyboardInterrupt:
		circuit.stop()
