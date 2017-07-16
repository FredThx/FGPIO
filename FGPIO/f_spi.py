#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
	Utilisation du protocole SPI
		- Soit en approche matérielle (hardware SPI)
			utilisation des pins standards et spidev
		- Soit en approche logitiel (bit banged spi)
			gestion en python de tout et choix de n'importe quelle pin
	
 AUTEUR : FredThx

 Projet : rpiduino_io

'''

import spidev
import time

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
		spidev.SpiDev.__init__(self)
		self.open(bus, device)

