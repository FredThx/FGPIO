#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
 Gestion des modules MPC3008
	pour création entrée analogique
	sur un rpiduino_io
		- Rpi
		- pcduino
	
	Gestion du protocole SPI : logitiel (100% python)
		
	Wiring :
		        _ _
			   | U |
		CH0 ---|   |--- Vdd : 2.7V - 5V
		CH1 ---|   |--- Vref
		CH2 ---|   |--- 0V (circuit analogique)
		CH3 ---|   |--- CLK : pin_clock
		CH4 ---|   |--- Dout : pin_miso
		CH5 ---|   |--- Din : pin_mosi
		CH6 ---|   |--- CS : pin_cs
		CH7 ---|   |--- 0V (circuit digital)
		       |___|
			   
	CH0-CH7 : analog inputs
	
 AUTEUR : FredThx

 Projet : rpiduino_io

'''
#TODO :
#	-	creer une sur-classe SPI
#	-	se poser la question de la fréquence (ici, pas de time.sleep) : fréquence non maitrisée

from rpiduino_io import *

class mcp300x_io(device_io):
	'''Classe pour convertisseur analogique/numérique MCP3004/MCP3008
	'''
	def __init__(self, pin_clock, pin_miso, pin_mosi, pin_cs, vref = 3.3):
		'''Initialisation
			pin_clock		:	a digital_pin_io
			pin_mosi		:	a digital_pin_io
			pin_miso		:	a digital_pin_io
			pin_cs			:	a digital_pin_io
			Vref			:	ref voltage
		'''
		self.pin_clock = pin_clock
		self.pin_mosi = pin_mosi
		self.pin_miso = pin_miso
		self.pin_cs = pin_cs
		self.pin_clock.setmode(OUTPUT)
		self.pin_mosi.setmode(OUTPUT)
		self.pin_miso.setmode(INPUT)
		self.pin_cs.setmode(OUTPUT)
		self.pin = {}
		self.vref = vref

class mcp3004_io(mcp300x_io):
	'''Classe pour convertisseur analogique/numérique MCP3004
	'''
	def __init__(self, pin_clock, pin_mosi, pin_miso, pin_cs, vref = 3.3):
		'''Initialisation
			pin_clock		:	a digital_pin_io
			pin_mosi		:	a digital_pin_io
			pin_miso		:	a digital_pin_io
			pin_cs			:	a digital_pin_io
			Vref			:	ref voltage
		'''
		mcp300x_io.__init__(self, pin_clock, pin_mosi, pin_miso, pin_cs, vref)
		for i in range(4):
			self.pin[i] = mcp300x_pin(self, i)
		
	
	
class mcp3008_io(mcp300x_io):
	'''Classe pour convertisseur analogique/numérique MCP3008
	'''
	def __init__(self, pin_clock, pin_mosi, pin_miso, pin_cs, vref = 3.3):
		'''Initialisation
			pin_clock		:	a digital_pin_io
			pin_mosi		:	a digital_pin_io
			pin_miso		:	a digital_pin_io
			pin_cs			:	a digital_pin_io
			Vref			:	ref voltage
			'''
		mcp300x_io.__init__(self, pin_clock, pin_mosi, pin_miso, pin_cs, vref)
		for i in range(8):
			self.pin[i] = mcp300x_pin(self, i)

class mcp300x_pin(analog_pin_io):
	'''Une pin analogique sur mcp3004/3008
	'''
	def __init__(self, mcp300x_ship, chanel):
		'''Initialisation
			mcp300x_ship	:	a mcp300x_io
			chanel			:	n° of the input chanel
		'''
		self.ship = mcp300x_ship
		self.chanel = chanel
	
	def get(self):
		''' get the raw value of the input chanel
		'''
		self.ship.pin_cs.set(HIGH)
		self.ship.pin_clock.set(LOW)
		self.ship.pin_cs.set(LOW)
		command = self.chanel | 0x18
		command <<= 3	#only 5 bits
		for i in range(5):
			if (command & 0x80):
				self.ship.pin_mosi.set(HIGH)
			else:
				self.ship.pin_mosi.set(LOW)
			command <<= 1
			self.ship.pin_clock.set(HIGH)
			self.ship.pin_clock.set(LOW)
		result = 0
		for i in range(12):
			self.ship.pin_clock.set(HIGH)
			self.ship.pin_clock.set(LOW)
			result <<=1
			if (self.ship.pin_miso.get()):
				result |= 0x1
		self.ship.pin_cs.set(HIGH)
		return result / 2
	
	def get_voltage(self):
		''' get the voltage on the input chanel
		'''
		return self.get() * self.ship.vref / 1024.
	

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	mcp3008 = mcp3008_io(*pc.bcm_pins(18,23,24,25), vref=5)
	ch0 = mcp3008.pin[7]
	while True:
		print 'Voltage : %.2f Volts' % ch0.get_voltage()
		time.sleep(0.5)
