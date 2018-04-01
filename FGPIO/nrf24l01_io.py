#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
 Gestion du module Emetteur-Recepteur 2.4GHz
		NRF24L01+
		avec rpiduino_io
	branché en série SPI
	
Branchement :
	
	Vue de dessus :
	___________________
	|1 2		_____  |
	|3 4		|____  |
	|5 6		_____| |
	|7 8  [==]  |____  |
	-------------------
	
				raspberry
	1 - 0V		
	2 - 3.3V
	3 - CE
	4 - CSN
	5 - SCK
	6 - MOSI
	7 - MISO
	8 - NA (= IRQ)
	
	
	
 AUTEUR : FredThx

 Projet : rpiduino_io

'''


from f_spi import *


class nrf24l01_io(hard_spi_client):
	''' Emetteur-Recepteur 2.4GHz NRF24L01+ branché en série SPI
	'''
	def __init__(self,  bus=0, device=0):
		'''Initialisation
			- bus		:	n° du bus où est branché le module
			- device	:	n° du module sur le bus
		'''