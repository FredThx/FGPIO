#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# Moteur pas à pas
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
#################################### 

import time
from rpiduino_io import *
from f_thread import *


class stepper_io(device_io):
	''' Stepper motor like 28BYJ-48
	
		usage :
				pc = rpiduino_io()
				motor = stepper_io(pc.bcm_pins(12,16,20,21))
				
			simple :
				motor.rotate(180)
				motor.totate(180, speed = 5)
				
			with threading :
				def myFunction(result):
					if result:
						print("Rotation donne.")
					else:
						print("Arrggg, something stop me!")
				motor.rotate(360, thread = True, callback = myFunction)
				
	'''
	seq = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]
	min_delay = 0.8/1000
	
	def __init__(self, step_pins, steps_360 = 4096, speed = 15):
		'''Initialisation
			- step_pins			:	list of digital_pin_io
			- steps_360			:	nb of step for 360° (default : 4092)
			- speed				:	revolution per minutes (default : 20)
		'''
		assert isinstance(step_pins, list), 'step_pins must be a list'
		assert len(step_pins)==4,'step_pins must be a list of 4'
		self.step_pins = step_pins
		for pin in self.step_pins:
			assert isinstance(pin,digital_pin_io), 'step pin must be a digital_pin_io'
			pin.setmode(OUTPUT)
			pin.set(LOW)
		self.steps_360 = steps_360
		self.stepcount = len(self.seq)
		self.phase = 1
		self.speed = speed
		self.direction = 0 
		self.step_counter = 0
		self.init()
		self.thread=None
	
	def init(self, position = 0):
		''' Initialise the position
			- position		:	position in steps (optionnal)
		'''
		self._position = position
	
	@property
	def position(self):
		'''get the position
		'''
		return self._position
		
	@property
	def status(self):
		'''Return 
			-1 if the motor is running counterclockwise 
			+1 if the motor is running clockwise
			0 if the motor is stopped
		'''
		return self.direction
		
	def read(self):
		'''For device_io
		'''
		return self.position
	
	
	def rotate(self, angle, speed = None, callback = None, thread = False):
		'''Rotate to
			- angle		:	angle in degree 
								- >0 : clockwise
								- <0 : counterclockwise 
			- speed		:	??
			- callback	:	callback function with 1 argument (result)
		'''
		self.stop()
		self.step_counter = 0
		if angle > 0:
			self.direction = 1
		elif angle < 0:
			self.direction = -1
		else:
			self.direction = 0
		if speed:
			self.speed = speed
		self.time_per_step = 60.0/(self.steps_360 * self.speed)
		if self.time_per_step < self.min_delay:
			logging.warning('Unable to rotate so fast, speed is reduced')
			self.time_per_step = self.min_delay
		self.max_counter = abs(angle * self.steps_360 / 360)
		self.callback = callback
		if thread:
			self.thread = f_thread(self.rotate_one_step)
			self.thread.start()
		else:
			self.thread = None
			while self.rotate_one_step():
				pass
			self.direction = 0
			if callback:
				self.callback(abs(self.step_counter) >= self.max_counter)
 
	def rotate_one_step(self):
		time_next_step = time.time() + self.time_per_step
		self.step_counter += self.direction
		self._position += self.direction
		self.phase += self.direction
		self.phase %= self.stepcount
		for i,level in enumerate(self.seq[self.phase]):
			self.step_pins[i].set(level)
		if abs(self.step_counter) >= self.max_counter:
			if self.thread:
				self.stop()
				if self.callback:
					self.callback(True)
			return False
		time.sleep(abs(time_next_step-time.time()))
		return True
	
	def stop(self):
		'''Stop the rotation (if threading mode)
		'''
		if self.thread:
			self.thread.stop()
			if self.callback and abs(self.step_counter) < self.max_counter:
				self.callback(False)			
			self.direction = 0
	
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import sys
	pc = rpiduino_io()
	motor = stepper_io(pc.bcm_pins(12,16,20,21))
	print("90 degres counterclockwise")
	motor.rotate(-90)
	def myFunction(result):
		if result:
			print("Rotation donne.")
		else:
			print("Arrggg, something stop me!")
	print("360 degres")
	motor.rotate(360,speed = 18, thread = True, callback = myFunction)
	while motor.status:
		print("Position moteur : %s"%motor.position)
		time.sleep(0.25)
