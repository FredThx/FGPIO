#!/usr/bin/env python
# -*- coding:utf-8 -*

"""
# Ultrasonic sensor for mesuring distance
#
#	wiring :
#		- pin n°3 on a analogue_pin
			(hrlv_max_sonar_analog_io)
#	OR
#		- pin n°2 on a digital_pin for Pulse Width Output
			(hrlv_max_sonar_pwo_io)
#
# AUTHOR : FredThx
#
# Project : rpiduino_io
#
"""

from device_io import *
from pin_io import *
import time
import logging


class hrlv_max_sonar_io(analog_input_device_io):
	'''a HRLV MAX SONAR sensor
	'''
	pass

class hrlv_max_sonar_analog_io(hrlv_max_sonar_io):
	''' a HRLV MAX SONAR sensor readed by a analogue input pin
	'''
	scale = 5 * 1024.0 #5mm per Vcc/1024 volt
	def __init__(self, pin, vcc = None, seuil = 500, thread = False, on_changed = None, discard = None , pause = 0.1, timeout = 10):
		''' Initialisation
				-pin			:	a analog_pin_io
				-vcc			:	voltage on pin 6
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
		assert isinstance(pin, analog_pin_io), "pin must be a analog_pin_io"
		self.pin = pin
		if vcc == None:
			self.vcc = self.pin.vref
		else:
			self.vcc = vcc
		analog_input_device_io.__init__(self, seuil, thread, on_changed, discard, pause, timeout)
		logging.info("hrlv_max_sonar_analog_io created on pin %s." % self.pin)

	def read(self):
		''' Return the distance en mm
		'''
		return int(self.pin.get_voltage()/self.vcc * self.scale)

class hrlv_max_sonar_pwo_io(hrlv_max_sonar_io):
	''' a HRLV MAX SONAR sensor readed by a Pulse Width Output
	'''
	scale = 1.0 * 1000000. #1µs / mm
	read_timeout = 1
	def __init__(self, pin, seuil = 500, thread = False, on_changed = None, discard = None , pause = 0.1, timeout = 10):
		''' Initialisation
				-pin			:	a analog_pin_io
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
		assert isinstance(pin, digital_pin_io), "pin must be a digital_pin_io"
		self.pin = pin
		self.pin.setmode(INPUT)
		analog_input_device_io.__init__(self, seuil, thread, on_changed, discard, pause, timeout)
		logging.info("hrlv_max_sonar_pwo_io created on pin %s." % self.pin)

	def read(self):
		''' Return the distance in mm
		'''
		timeout = time.time() + self.read_timeout
		while self.pin.get()==LOW and time.time() < timeout:
			pass
		debut = time.time()
		while self.pin.get()==HIGH and time.time() < timeout:
			pass
		if time.time() < timeout:
			return (time.time()-debut)*self.scale
		else:
			logging.warning("Timeout on %s.read()." % self)


#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	from rpiduino_io import *
	pc = rpiduino_io()

	if isinstance(pc, pcduino_io):
	# Avec le pcduino, on utilisera plutot le mode analogique
		pin = pc.pin['A5']
		sonar = hrlv_max_sonar_analog_io(pin)
	else:# Cas du Rpi : on utilisera le mode PWO
		#from mcp300x_hspi_io import *
		#mcp3008 = mcp3008_hspi_io() (aussi possible en mode analogique avec un module mcp3008)
		pin = pc.pin[7]
		sonar = hrlv_max_sonar_pwo_io(pin)

	while True:
		print(sonar.read())
