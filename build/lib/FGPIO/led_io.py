#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# LED branchée sur un rpi_duino_io
# 
#    
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
#################################### 

from on_off_output_device_io import *

#TODO : utiliser le mode PWM pour faire varier l'intensité lumineuse.
# voir en bas : début
# mais il faut plutôt créer des pin_io de type analogique output
# et bien gérer à la fois pcduino et Rpi

class led_io (on_off_output_device_io):
	''' LED branchée sur un rpiduino (pcduino ou Rpi)
	'''
	def none_none(fonction):
		'''Décorateur : si pin==None : la fonction ne s'applique pas
		'''
		@functools.wraps(fonction) # ca sert pour avoir un help(SBClient) utile
		def none_none_fonction(self, *args, **kwargs):
			if self.pin == None:
				return None
			else:
				return fonction(self, *args, **kwargs)
		return none_none_fonction

# class pwm_led_io(device_io):
	# '''Une class pour piloter une led en PWM (Pulse Width Modulation
	# '''
	# def __init__(self, pin = None, intensite = 50, freq = 50):
		# '''Initialisation
			# - pin		:	digital_pin_io
			# - freq		:	frequency of the signal
			# - duty		:	%duration high
		# '''
		# if pin == None:
			# self.pin = None
		# else:
			# assert isinstance(pin, digital_pin_io), 'pin must be a digital_pin_io'
			# self.pin = pin
			# self.pin.setmode(PWM)
			
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	pin = pc.pin[40]
	LED = led_io(pin)
	none_led = led_io()
	LED.on()
	none_led.on() # Do nothing!
	time.sleep(1)
	LED.off()
	time.sleep(1)
	for i in range(0,5):
		LED.invert()
		print "la LED est " + str(LED.get())
		time.sleep(1)
	LED.blink()		# blink 1 second / 1 second
	time.sleep(5)
	LED.blink(0.1,0.2)	# Accelerate the blinking
	time.sleep(5)
	LED.stop()		# Stop the blinking
	