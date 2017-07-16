#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# A on_off simple output device for rpi_duino_io (Rpi or pcduino)
# 
#    exemple : led, buzzer, relay, ...
#
#	Do not use this abstract class, but 
#		- led_io
#		- buzz_io
#		- relay_io
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
#################################### 

import time
import functools
from rpiduino_io import *
import logging



class on_off_output_device_io (device_io):
	''' on/off output device wired on a rpiduino (pcduino ou Rpi)
	'''
	default_blink_time_on = 1
	
	def __init__(self, pin=None):
		''' Initialisation
				pin	:	digital_pin_io
						(is None ou omis, the device if inactive
		'''
		if pin==None:
			self.pin = None
		else:
			if isinstance(pin, digital_pin_io):
				self.pin = pin
				self.pin.setmode(OUTPUT)
			else:
				raise rpiduino_io_error('argument error : pin must be a digital_pin_io.')
		self.thread = None
		thread_end_time = None
		logging.info("%s is created on pin %s." % (self, self.pin))
	
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
	def set(self, etat):
		''' change the state of the device
			state	:	False / True
		'''
		if etat:
			self.pin.set(HIGH)
		else:
			self.pin.set(LOW)
	
	@none_none
	def get(self):
		''' get the device state
		'''
		return self.pin.get()
	
	@none_none
	def on(self):
		''' Set on the device
		'''
		self.set(True)
	
	@none_none
	def off(self):
		''' Set off the device
		'''
		self.set(False)
	
	@none_none
	def invert(self):
		''' Invert the device state
		'''
		self.pin.invert()
	
	@none_none
	def blink(self, time_on = None, time_off = None, time_end = None):
		''' Create a thread for blinking the device
			- time_on	:	duration led is on (second)
			- time_off	:	duration led is off (second)
			- time_end	:	stop the thread after time_end seconds
							if time_end = None (default) the thread do not stop.
		'''
		if time_on == None:
			time_on = self.default_blink_time_on
		self.th_time_on = time_on
		if time_off == None:
			self.th_time_off = time_on
		else:
			self.th_time_off = time_off
		if self.thread == None:
			self.thread = f_thread(self._blink)
			if time_end==None:
				self.thread_end_time = None
			else:
				self.thread_end_time = time.time() + time_end
			self.thread.start()

	def _blink(self):
		self.on()
		time.sleep(self.th_time_on)
		self.off()
		time.sleep(self.th_time_off)
		if self.thread_end_time!=None and time.time() > self.thread_end_time:
			self.stop()
	
	
	@none_none
	def stop(self):
		''' Stop blinking the device
		'''
		if self.thread:
			self.thread.stop()
			self.thread = None
		self.off()
	