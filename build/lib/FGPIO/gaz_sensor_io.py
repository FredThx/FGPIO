#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
Gaz Sensor v1.3
	with MQ-7 sensor
	for CO mesurement

	wiring :	pin 1 (GND)		:	0V
				pin 2 (DOUT)	:	Digital Out : a digital_pin_io
				pin 3 (AOUT)	:	Analog Out : a analog_pin_io
				pin 4 (VCC)		:	5V

	Note : sensor can be use with
		- Digital out	:	digital_gaz_sensor_MQ7_io
		- Analogue out  : 	analog_gaz_sensor_MQ7_io

 AUTHOR : FredThx

 Project : rpiduino_io

'''

from rpiduino_io import *

class gaz_sensor_MQ7(device_io):
	''' A gaz sensor v1.3 with MQ-7 sensor
	'''
	def __init__(self):
		pass

class digital_gaz_sensor_MQ7_io(gaz_sensor_MQ7, digital_input_device_io):
	'''A gaz sensor v1.3 with MQ-7 sensor
		on digital mode (on/off mode)
	'''
	def __init__(self, pin, thread = False, on_changed = None, pause = 0.1):
		'''Initialisation
			pin		:	digital_pin_io (DOUT)
		'''
		assert isinstance(pin, digital_pin_io), 'pin must be a digital_pin_io'
		self.pin = pin
		self.pin.setmode(PULLUP)
		digital_input_device_io.__init__(self, thread, on_changed, pause)

	def read(self):
		'''Get the sensor status
			True	:	High %CO
			False	:	Low %CO
		'''
		return self.pin.get()==LOW


class analog_gaz_sensor_MQ7_io(gaz_sensor_MQ7, analog_input_device_io):
	'''A gaz sensor v1.3 with MQ-7 sensor
		on analog mode with AOUT pin
	'''
	def __init__(self, pin, dth11 = None, seuil=2000, thread = False, on_changed = None, discard = None , pause = 0.1, timeout = 10):
		'''Initialisation
			- pin		:	analog_pin_io (AOUT)
			- seuil 		:	seuil de detection
								soit un tuple (seuil_bas, seuil_haut)
								soit une seule valeur
			- thread		:	(facultatif) True si utilisation thread
			- on_changed	:	fonction ou string executable
								qui sera lancée quand la valeur du capteur change
			- discard		:	ecart en dessous duquel une valeur est considérée comme inchangée
			- pause 		:	pause entre chaque lecture du composant
			- timeout		:	durée après laquelle une valeur lue est obsolète
		'''
		assert isinstance(pin, analog_pin_io), 'pin must be a analog_pin_io.'
		self.pin = pin
		if dth11!=None:
			assert isinstance(dth11, dht11_io), 'dth11 must be a dht11_io.'
		self.dth11 = dth11
		analog_input_device_io.__init__(self, seuil, thread, on_changed, discard, pause, timeout)

	def read(self):
		'''Renvoie le taux de CO en ppm
		'''
		#TODO : gestion correction température et humidité (dth11)
		#TODO : calculer la concentration : pour l'instant : en renvoie la valeur brute
		return self.pin.get()

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	CO_detector = digital_gaz_sensor_MQ7_io(pc.logical_pin(2))

	def action_sensor_change():
		if CO_detector.th_readed():
			print('ALERTE : %CO is too high. Open the windows!')
		else:
			print('END OF ALERTE. You can close the windows.')

	CO_detector.add_thread(on_changed = action_sensor_change, pause = 1)

	CO_sensor = analog_gaz_sensor_MQ7_io(pc.pin['A2'])


	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			print(CO_sensor.read())
			time.sleep(1)
	except KeyboardInterrupt:
		CO_detector.stop()
