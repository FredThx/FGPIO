#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# Buzzer branchée sur un rpi_duino_io
# 
#   buzz_io		:	simple buzzer
#	pwm_buzz_io	:	buzzer with pwm signal
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
#################################### 

from on_off_output_device_io import *


class buzz_io (on_off_output_device_io):
	''' Buzzer branchée sur un rpiduino (pcduino ou Rpi)
	'''
	
	#Delete inherited methods
	blink = None
	_blink = None
	
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
	
	@none_none
	def bip(self, duration = 0.5):
		''' Bip once
		'''
		self.on()
		time.sleep(duration)
		self.off()
	
	@none_none
	def bip_bip(self, time_on = 1, time_off = None, time_end = None):
		''' Create a thread for send a bip_bip sound
			- time_on	:	duration buzz is on (second)
			- time_off	:	duration buzz is off (second)
			- time_end	:	stop the thread after time_end seconds
							if time_end = None (default) the thread do not stop.
		'''
		self.th_time_on = time_on
		if time_off == None:
			self.th_time_off = time_on
		else:
			self.th_time_off = time_off
		if self.thread == None:
			self.thread = f_thread(self._bip_bip)
			if time_end==None:
				self.thread_end_time = None
			else:
				self.thread_end_time = time.time() + time_end
			self.thread.start()

	def _bip_bip(self):
		self.on()
		time.sleep(self.th_time_on)
		self.off()
		time.sleep(self.th_time_off)
		if self.thread_end_time!=None and time.time() > self.thread_end_time:
			self.stop()
	

class pwm_buzz_io(buzz_io):
	'''Une class pour piloter un buzzer en PWM (Pulse Width Modulation)
	'''
	def __init__(self, pin = None, duty_cycle = 50, freq = 50):
		'''Initialisation
			- pin		:	digital_pin_io
			- freq		:	frequency of the signal
			- duty		:	%duration high
		'''
		if pin == None:
			self.pin = None
		else:
			assert isinstance(pin, digital_pin_io), 'pin must be a digital_pin_io'
			self.pin = pin
		self.freq = freq
		self.duty_cycle = duty_cycle
		self.pin.set_pwm(freq)
		self.thread = None
		thread_end_time = None
		logging.info("pwm_buzz_io is created on pin %s." % self.pin)
	
	def set(self, etat):
		''' change l'état du buzzer
			etat	:	False / True
		'''
		if etat:
			self.pin.start_pwm(self.duty_cycle)
		else:
			self.pin.stop_pwm()
	
	def get(self):
		''' Récupère l'état du buzzer
		'''
		fin = time.time() + (1 / self.freq)
		while time.time() < fin:
			if self.pin.get():
				return HIGH
		return LOW
	
	def set_freq(self, freq):
		''' Change the frequency
		'''
		self.pin.set_freq_pwm(freq)
		
	def set_duty(self, duty_cycle):
		'''Change the duty_cycle percent
			- duty_cycle	:	0-100
		'''
		self.duty_cycle = duty_cycle
		self.pin.set_duty_pwm(duty_cycle)
	
	def hoot(self, period = 1, time_end = None):
		''' Create a thread for send a hooter sound
			- period	:	period of the hoot
			- time_end	:	stop the thread after time_end seconds
							if time_end = None (default) the thread do not stop itself
		'''
		if self.thread == None:
			self.thread = f_thread(self._hoot, period)
			if time_end==None:
				self.thread_end_time = None
			else:
				self.thread_end_time = time.time() + time_end
			self.thread.start()
			
	def _hoot(self, period = 1):
		self.on()
		for freq in range(500,3000,100) + range(3000,500, -100):
			self.set_freq(freq)
			time.sleep(period/50.)
		if self.thread_end_time!=None and time.time() > self.thread_end_time:
			self.stop()
			
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	buzzer = pwm_buzz_io(pc.bcm_pin(25))
	buzzer.bip()
	time.sleep(5)
	buzzer.bip_bip(time_end = 10)
	

	
	