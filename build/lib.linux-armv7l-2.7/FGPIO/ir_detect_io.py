#!/usr/bin/env python
# -*- coding:utf-8 -*


"""
# Digital Infra Red motion sensor as UI.R. SEN0018 of DFROBOT
# 
#	wiring :	a pin on 0V
#				a pin on 3.3V
#				a pin on a digital io
#
#	on SEN0018, set the jumper at L, and the potentiometer as you need detection sensitivity
#
# AUTHOR : FredThx
#
# Project : rpiduino_io
#
"""


from rpiduino_io import *
import time
import logging

class ir_detect_io(digital_input_device_io):
	''' Digital Infra Red motion sensor branché sur un rpiduino (pcduino ou Rpi)
	'''
	def __init__(self, pin, thread = False, on_changed = None, pause = 0.1, detection_time = 5):
		''' Initialisation
				- pin			:	digital_pin_io
				- thread		:	(facultatif) True si utilisation thread
				- on_changed	:	deamon quand le capteur change
				- pause			:	pause (secondes) entre chaque lecture du composant
				- detection_time:	temps durant lequel une detection est active
		'''
		if isinstance(pin, digital_pin_io):
			self.pin = pin
			self.pin.setmode(INPUT)
		else:
			raise rpiduino_io_error('argument erreur : n''est pas du type digital_pin_io')
		digital_input_device_io.__init__(self, thread, on_changed, pause)
		self.detection_time = detection_time
		self.detected = False
		self.time_last_detection = None
		logging.info("%s is created on pin %s. " % (self, self.pin))
	
	def get(self):
		''' Récupère l'état du capteur sous la forme LOW/HIGH
		'''
		return self.pin.get()
		
	@property
	def is_detected(self):
		''' Renvoie True s'il y a une detection, False sinon
		'''
		if self.get() == HIGH:
			self.time_last_detection = time.time()
			self.detected = True
		elif self.detected:
			if self.time_last_detection + self.detection_time > time.time():
				self.detected = True
			else:
				self.detected = False
		return self.detected
	
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
	d = ir_detect_io(pc.bcm_pin(21))
	def action_detector_change():
		if d.th_readed():
			print "Detection!!."
		else:
			print "no detection."
	d.add_thread(action_detector_change)

	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		d.stop()