#!/usr/bin/env python
# -*- coding:utf-8 -*


####################################
'''
# Gestion de composants i2c
#			basée sur la lib smbus
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
####################################


import smbus
import time


class i2c_device:
	""" Composant i2c
	"""
	def __init__(self, addr=None, bus=1):
		"""Initialise le composant i2c
			addr : adresse (exemple : 0x20) Si addr==None, on scan le bus et choisit le premier qui repond
			bus : n° du bus (1,2,...)
		"""
		self.bus = i2c_bus(bus)
		if addr==None:	# Si l'adresse sur le bus n'est pas fournit, recherche ...
			addrs = self.bus.scan()
			if len(addrs)>0:
				self.addr = addrs[0]
		else:
			self.addr = addr
	
	
	def write_cmd(self, cmd):
		''' Write a single command
		'''
		self.bus.smbus.write_byte(self.addr, cmd)
		time.sleep(0.0001)
	
	
	def write_cmd_arg(self, cmd, data):
		''' Write a command and argument
		'''
		self.bus.smbus.write_byte_data(self.addr, cmd, data)
		time.sleep(0.0001)
	
	
	def write_block_data(self, cmd, data):
		''' Write a block of data.
		'''
		self.bus.smbus.write_block_data(self.addr, cmd, data)
		time.sleep(0.0001)
	
	def write_word_data(self, cmd, data):
		'''Write a word 
		'''
		self.bus.smbus.write_word_data(self.addr, cmd, data)
		time.sleep(0.0001)
	
	def read(self):
		''' Read a single byte. False if IOError
		'''
		try:
			return self.bus.smbus.read_byte(self.addr)
		except IOError:
			return False
	
	
	def read_data(self, cmd):
		''' Read. False if IOError
		'''
		try:
			return self.bus.smbus.read_byte_data(self.addr, cmd)
		except IOError:
			return False
	
	
	def read_block_data(self, cmd):
		''' Read a block of data. False if IOError
		'''
		try:
			return self.bus.smbus.read_block_data(self.addr, cmd)
		except IOError:
			return False
	
	def read_i2c_block_data(self, cmd, len):
		''' Read i2c datas
		'''
		try:
			return self.bus.smbus.read_i2c_block_data(self.addr, cmd, len)
		except IOError:
			return False

class i2c_bus():
	"""Bus i2c"""
	def __init__(self, port):
		"""Initialisation
		"""
		self.smbus = smbus.SMBus(port)
		
	def scan(self):
		"""Scan le bus et renvoie la liste des adress valides
		"""
		liste=[]
		for addr in range(0x03, 0x77):
			try:
				self.smbus.write_quick(addr)
			except:
				pass
			else:
				liste.append(addr)
		return liste
		
################################
#                              #
#    GESTION DES ERREURS       #
#                              #
################################
		
class i2c_error(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return self.message