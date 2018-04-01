#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
 Gestion des modules MPC3008
	pour création entrée analogique
	sur un rpiduino_io
		- Rpi
		- pcduino
	
	Gestion du protocole SPI : hardware spi
		
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
from f_spi import *

class mcp300x_hspi_io(device_io, hard_spi_client):
	'''Classe pour convertisseur analogique/numérique MCP3004/MCP3008
	'''
	def __init__(self, bus, device, vref = 3.3):
		'''Initialisation
			bus		:	spi bus (0|1)
			device	:	no spi client (0 : CS = CE0 = GPIO08 | 1 : CS = CE1 = GPIO07)
			Vref	:	ref voltage
		'''
		hard_spi_client.__init__(self, bus, device)
		self.pin = {}
		self.vref = vref

class mcp3004_hspi_io(mcp300x_hspi_io):
	'''Classe pour convertisseur analogique/numérique MCP3004
	'''
	def __init__(self, bus=0, device=0, vref = 3.3):
		'''Initialisation
			bus		:	spi bus (0|1)
			device	:	no spi client
			Vref			:	ref voltage
		'''
		mcp300x_hspi_io.__init__(self, bus, device, vref)
		for i in range(4):
			self.pin[i] = mcp300x_hspi_pin(self, i)
		
class mcp3008_hspi_io(mcp300x_hspi_io):
	'''Classe pour convertisseur analogique/numérique MCP3008
	'''
	def __init__(self, bus=0, device=0, vref = 3.3):
		'''Initialisation
			bus		:	spi bus
			device	:	no spi client
			Vref			:	ref voltage
		'''
		mcp300x_hspi_io.__init__(self, bus, device,  vref)
		for i in range(8):
			self.pin[i] = mcp300x_hspi_pin(self, i)

class mcp300x_hspi_pin(analog_pin_io):
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
		result = self.ship.xfer2([1,(8+self.chanel)<<4,0])
		result = ((result[1]&3) << 8) + result[2]
		return result
	
	def get_voltage(self):
		''' get the voltage on the input chanel
		'''
		return self.get() * self.ship.vref / 1024.
	
	@property
	def vref(self):
		return self.ship.vref

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	mcp3008 = mcp3008_hspi_io()
	ch0 = mcp3008.pin[7]
	while True:
		print 'Voltage : %.2f Volts' % ch0.get_voltage()
		time.sleep(0.5)
