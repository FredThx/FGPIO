#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# Servor moteur
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
#################################### 

import time
from rpiduino_io import *


class servo_motor(device_io):
	'''Servomoteur using PWM
	'''
	frequency = 50
	delay_move = 0.7
	def __init__(self, cmd_pin, ctrl_pin = None):
		'''Initialisation
			- cmd_pin	:	a digital_pin_io
			- ctrl_pin	:	a analog_pin_io for mesuring position
		'''
		assert isinstance(cmd_pin, digital_pin_io)
		self.cmd_pin = cmd_pin
		if ctrl_pin != None:
			assert isinstance(ctrl_pin, analog_pin_io)
		self.ctrl_pin = ctrl_pin
	
	@staticmethod
	def _reg_line(x, delta_x, delta_y):
		if len(delta_x)>2:
			if x < delta_x[1]:
				return servo_motor._reg_line(x, delta_x[:2], delta_y[:2])
			else:
				return servo_motor._reg_line(x, delta_x[1:], delta_y[1:])
		else:
			return delta_y[0] + (delta_y[1]-delta_y[0])*(x-delta_x[0])/(delta_x[1]-delta_x[0])
	
	def get_position(self):
		'''Get the angular position
		'''
		assert self.ctrl_pin != None, 'The ctrl_pin must not be None to get position'
		return self._reg_line(self.ctrl_pin.get_voltage(), self.voltage_ctrl_pin, self.angle)
	
	def set_position(self, angle):
		'''Positionne le servomoteur selon un angle
			- angle		:	angle between 0 and 180°
		'''
		assert (self.angle[0]<=angle<=self.angle[2]), 'angle must be in range : (%s,%s)' % (self.angle[0],self.angle[2])
		self.cmd_pin.set_pwm(self.frequency)
		if self.ctrl_pin==None:
			duty_cycle = self._reg_line(angle, self.angle, self.duty_cycle_cmd_pin)
			print 'angle : %s - duty_cycle : %s' % (angle, duty_cycle)
			self.cmd_pin.start_pwm(duty_cycle)
			time.sleep(self.delay_move)
		else:
			angle0 = self.get_position()
			sens = abs(angle - angle0)/(angle - angle0)
			duty_cycle0 = self._reg_line(angle0, self.angle, self.duty_cycle_cmd_pin)
			duty_cycle = self._reg_line(angle, self.angle, self.duty_cycle_cmd_pin)
			duty_cycle = (duty_cycle + duty_cycle0)/2
			self.cmd_pin.start_pwm(duty_cycle)
			time.sleep(self.delay_move/2)
			while self.get_position()*sens < angle*sens:
				print self.get_position()*sens, angle*sens, duty_cycle, sens
				duty_cycle+=0.01 * sens
				self.cmd_pin.set_freq_pwm(50)
				self.cmd_pin.set_duty_pwm(duty_cycle)
				time.sleep(0.1)
					
		self.cmd_pin.stop_pwm()
		
class S1123_servo_motor(servo_motor):
	'''Servomoteur BATAN S1123
	'''
	frequency = 50
	angle = (0, 90, 180)
	voltage_ctrl_pin = (0.13, 1.19, 2.47)
	duty_cycle_cmd_pin = (1., 4.5, 10.)
	def __init__(self, cmd_pin, ctrl_pin = None):
		'''Initialisation
			- cmd_pin	:	a digital_pin_io
			- ctrl_pin	:	a analog_pin_io for mesuring position
		'''
		servo_motor.__init__(self,cmd_pin, ctrl_pin)
	
			
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	from mcp300x_hspi_io import *
	pc = rpiduino_io()
	mcp=mcp3008_hspi_io(0,0,5)
	sm=S1123_servo_motor(pc.pin[7], mcp.pin[0])
	print '0°'
	sm.set_position(0)
	time.sleep(1)
	print '90°'
	sm.set_position(90)
	time.sleep(1)
	print '180°'
	sm.set_position(180)
	time.sleep(1)
	print '45°'
	sm.set_position(45)
	
