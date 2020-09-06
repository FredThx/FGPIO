#!/usr/bin/env python
# -*- coding:utf-8 -*


"""
# IR motion sensor on a rpi_duino_io
#
#	wiring :	a pin on 0V
#				a pin on 5V
#				a pin on a digital io (0-3.3V)
#
# AUTHOR : FredThx
#
# Project : rpiduino_io
#
"""


from rpiduino_io import *
import logging

#TODO : fusionner avec classe ir_detect_io (qui gère en plus un temps d'attente déjà présent sur ce capteur)
# => un peu d'héritage....

class hcsr501_io(digital_input_device_io):
	''' Detecteur de mouvement Infra rouge HCSR501
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
			self.pin.setmode(INPUT)
		else:
			raise rpiduino_io_error('argument erreur : n''est pas du type digital_pin_io')
		digital_input_device_io.__init__(self, thread, on_changed, pause)
		logging.info("%s is created on pin %s. " % (self, self.pin))

	def get(self):
		''' Récupère l'état du capteur sous la forme LOW/HIGH
		'''
		return self.pin.get()

	@property
	def is_detected(self):
		''' Renvoie True s'il y a une detection, False sinon
		'''
		return self.get() == HIGH

	def read(self):
		''' Lecture, pour le thread, du bouton
		'''
		return self.is_detected

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	capteur = hcsr501_io(pc.bcm_pin(21))
	def action_sensor_change():
		if capteur.th_readed():
			print("Detection.")
		else:
			print("fin de detection.")
	capteur.add_thread(action_sensor_change)

	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		capteur.stop()
