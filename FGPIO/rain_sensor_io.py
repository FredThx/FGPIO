#!/usr/bin/env python
# -*- coding:utf-8 -*


"""
# Humidity Detection Sensor Module Rain Detection for Arduino
#
#	wiring :
#		- Vcc	:	3.3V (if 5V, add a voltage divider to protect IO)
#		- GRND	:	0V
#		- D0	:	a digital_pin_io
#		or
#		- A0	:	a analog_pin_io (for Rpi, use a MCP3008 module
#
# AUTHOR : FredThx
#
# Project : rpiduino_io
#
"""

#TODO : analog_input_device_io

from rpiduino_io import *
import logging

class rain_sensor_digital_io(digital_input_device_io):
	''' Humidity Detection sensor
	'''
	def __init__(self, pin, thread = False, on_changed = None, pause = 0.1):
		''' Initialisation
				- pin		:	digital_pin_io
				- thread	:	(facultatif) True si utilisation thread
				- on_changed:	deamon quand le capteur change
				- pause		:	pause entre chaque lecture du composant
		'''
		if isinstance(pin, digital_pin_io):
			self.pin = pin
			self.pin.setmode(PULLUP) # c'est à dire avec une résistance interne placée entre la pin et le +3.3V pour remettre à HIGH la pin quand non branchée
		else:
			raise rpiduino_io_error('argument erreur : n''est pas du type digital_pin_io')
		self.last_state= False
		digital_input_device_io.__init__(self, thread, on_changed, pause)
		logging.info("%s is created on pin %s. " % (self, self.pin))

	def get(self):
		''' Récupère l'état du capteur sous la forme LOW/HIGH
		'''
		return self.pin.get()

	def is_raining(self):
		''' renvoie True si le capteur détecte de la pluie
		'''
		return (self.pin.get()==LOW)

	def read(self):
		''' Lecture, pour le thread, du capteur
		'''
		return self.is_raining()



#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	sensor = rain_sensor_digital_io(pc.bcm_pin(23))
	def action_bt_change():
		global sensor
		if sensor.th_readed():
			print("It is raining!")
		else:
			print("Ok, no rain.")

	sensor.add_thread(action_bt_change)

	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			time.sleep(0.1)
	except KeyboardInterrupt:
		sensor.stop()
