#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
	Utilisation du protocole SPI
		- Soit en approche matérielle (hardware SPI)
			utilisation des pins standards et spidev
			
			SPI0 :
				- MOSI : GPIO10 (pin 19)
				- MISO : GPIO09 (pin 21)
				- SCLK : GPIO11 (pin 23)
				- CE0  : GPIO08 (pin 24)
				- CE1  : GPIO07 (pin 26)
			
			SPI1 :
				- MOSI : GPIO20 (pin 38)
				- MISO : GPIO19 (pin 35)
				- SCLK : GPIO21 (pin 40)
				- CE0  : GPIO18 (pin 12)
				- CE1  : GPIO17 (pin 11)
			
		- Soit en approche logitiel (bit banged spi)
			gestion en python de tout et choix de n'importe quelle pin
	
 AUTEUR : FredThx

 Projet : rpiduino_io

'''

import spidev
import time
import logging

class spi_client():
	'''A spi client
	'''
	def __init__(self):
		pass

class hard_spi_client(spi_client, spidev.SpiDev):
	'''A spi client manage by spidev
	'''
	def __init__(self, bus=0, device=0):
		'''Initialisation
			bus		:	0 for SPI0
						1 for SPI1
			device	:	0 for CE0
						1 for CE1
			link to /dev/spidev-bus.device
		'''
		assert bus in [0,1], "wrong spi bus %s, must be 0 (SPI0) or 1 (SPI1)."%(bus)
		assert device in [0,1], "wrong spi device %s, must be 0 (CE0) or 1 (CE1)."%(device)
		try:
			spidev.SpiDev.__init__(self)
			self.open(bus, device)
		except IOError:
			logging.error('Error openning spi bus %s'%(bus))

class soft_spi_client(spi_client):
	'''A spi software-pyhton client
	'''
	def __init__(self, pin_clock, pin_miso, pin_mosi, pin_cs):
		'''Initialisation
			pin_clock		:	a digital_pin_io
			pin_mosi		:	a digital_pin_io
			pin_miso		:	a digital_pin_io
			pin_cs			:	a digital_pin_io
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
		
	def read(self, command):
		''' Send command and read the device
		'''
		#TODO : a tester + adapter à MCP300x : voir autres
		self.pin_cs.set(HIGH)
		self.pin_clock.set(LOW)
		self.pin_cs.set(LOW)
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
		return result