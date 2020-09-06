#!/usr/bin/env python
# -*- coding:utf-8 -*
'''
 Gestion des modules MPC3201
	pour création entrée analogique
	sur un rpiduino_io
		- Rpi
		- pcduino

	Gestion du protocole SPI : hardware spi

	Wiring :
		        _ _
			   | U |						sur Rpi (SPI0):
	   Vref ---|   |--- Vdd : 2.7V - 5V			Vref : 3.3V (ou 5V, ou ...)
		IN+ ---|   |--- CLK						Vdd : 3.3V (ou 5V)
		IN- ---|   |--- Dout					CLK : SPI0_SCLK = GPIO11
		 0V ---|   |--- CS						Dout : SPI MISO = GPIO09
		       |___|							CS : - SPI0_CE0_N (GPIO08) => device = 0
													 - SPI0_CE1_N_N (GPIO07) => device = 1
 AUTEUR : FredThx

 Projet : rpiduino_io

 Dependances :
	spidev

'''
from rpiduino_io import *
from f_spi import *
from time import sleep

class mcp3201_hspi_io(analog_pin_io, hard_spi_client):
	'''
	Classe pour convertisseur analogique/numérique MCP3201
	'''
	def __init__(self, bus=0, device=0, vref = 3.3):
		'''
		Initialisation
			bus		:	spi bus (0|1)
			device	:	no spi client (0 : CS = CE0 = GPIO08 | 1 : CS = CE1 = GPIO07)
			Vref	:	ref voltage
		'''
		hard_spi_client.__init__(self, bus, device)
		analog_pin_io.__init__(self)
		self.vref = vref

	def get(self):
		'''
		Get the raw value of the input voltage
		'''
		#TODO : read all the bytes, check if null bit = 0, check if reverse data is correct...
		result = self.xfer2([0,0]) # read the two first bytes
		# result :
		#	[???,???,000,B11,B10,B09,B08,B07],[B06,B05,B04,B03,B02,B01,B00,B01]
		# => mask unused bits
		result = ((result[0] & 0b00011111) << 7) + ( result[1] >> 1)
		return result

	def get_voltage(self):
		''' get the voltage
		'''
		return self.to_voltage(self.get())

	def to_voltage(self, value):
		'''
		Return the voltage
			- value		:	raw value (from self.get())
		'''
		return value * self.vref / 4096.
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	#pc = rpiduino_io()
	mcp3201 = mcp3201_hspi_io()
	#Utilisation simple
	print('Voltage : %.2f Volts' % mcp3201.get_voltage())
	#Utilisation avec thread
	def on_changed(value):
		print("Voltage : %s"%(value))
	mcp3201.add_thread(on_changed)

	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			pass
	except KeyboardInterrupt:
		c.stop()
