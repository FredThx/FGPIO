#!/usr/bin/env python
# -*- coding:utf-8 -*



'''
Gestion des nano ordi pcduino et RPi

		pour utilisation de pleins de composants

AUTEUR : FredThx

Projet : rpiduino_io

'''


from pin_io import *
from device_io import *

# On essaye importer le module RPi.GPIO
try:
	import RPi.GPIO
except: # Si nous sommes sur un pcduino, ça ne marchera pas
	pass


INPUT = 0
OUTPUT = 1
PULLUP = 8
SERIAL = 40
I2C = 42
SPI = 41
HIGH = 1
LOW = 0


class rpiduino_io:
	'''
	Classe reprensentant soit
		pcduino_io	:	Une carte pcduino
		rpi_io		:	Une carte raspberry Pi
	'''
	def __init__(self):
		'''
		Initialisation du mini pc et de ces entrees-sortie
		Detecte s'il faut créer un pcduino_io ou un rpi_io
		Selon l'existance de la lib. RPi.GPIO
		'''
		try:
			RPi.GPIO # Test si la lib. GPIO est chargée (ie c'est un rpi)
			classe = rpi_io
		except NameError:
			classe = pcduino_io
		if classe == rpi_io:
			# On instancie un rpi_io
			self.__class__= rpi_io
			rpi_io.__init__(self)
		else:
			# On instancie un pcduino_io
			self.__class__= pcduino_io
			pcduino_io.__init__(self)

	def readall(self):
		'''Affiche l'état de toutes les pins
			et renvoie un dico avec les valeurs de chaques pins
		'''
		sortie = {}
		for k in self.pin:
			print(self.pin[k])
			sortie[k]=self.pin[k].get()
		return sortie

	def physical_pin(self, no_pin):
		''' Renvoie la pin_io nommés par son n° logique
		'''
		for pin in self.pin.values():
			if pin.physical_id==no_pin:
				return pin

	def physical_pins(self, *no_pins):
		''' Renvoie la liste des pins nommés par les n° physique
		'''
		pins = []
		for no_pin in no_pins:
			for pin in self.pin.values():
				if no_pin == pin.physical_id:
					pins.append(pin)
		return pins

	def logical_pin(self, no_pin):
		''' Renvoie la pin_io nommés par son n° logique
		'''
		for pin in self.pin.values():
			if pin.logical_id==no_pin:
				return pin

	def logical_pins(self, *no_pins):
		''' Renvoie la liste des pins nommés par les n° logique
		'''
		pins = []
		for no_pin in no_pins:
			for pin in self.pin.values():
				if no_pin == pin.logical_id:
					pins.append(pin)
		return pins

	def shutdown(self):
		'''Restart the system
		'''
		command = "/usr/bin/sudo /sbin/shutdown -r now"
		import subprocess
		process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

class pcduino_io(rpiduino_io):
	''' Classe pcduino
	'''
	def __init__(self):
		''' Initialisation d'un pcduino
			14 pins numeriques
			6 pins analogique dont
				2 sur 6 bits
				4 sur 12 bits
		'''
		self.modele = 'Pcduino'
		self.revision = None
		self.pin = {}
		for pin in range(0,14):
			self.pin[pin] = digital_puino_pin_io(pin)
		self.pin['A0'] = small_analog_puino_pin_io('A0')
		self.pin['A1'] = small_analog_puino_pin_io('A1')
		self.pin['A2'] = high_analog_puino_pin_io('A2')
		self.pin['A3'] = high_analog_puino_pin_io('A3')
		self.pin['A4'] = high_analog_puino_pin_io('A4')
		self.pin['A5'] = high_analog_puino_pin_io('A5')


class rpi_io(rpiduino_io):
	''' Classe Raspberry PI
	'''
	def __init__(self):
		''' Initialisation d'un RPI
		'''
		RPi.GPIO.setmode(RPi.GPIO.BCM)		#	Rpi.GPIO.BOARD ne fonctionne pas avec Rpi2 (malgré RPi.GPIO 0.5.11
		RPi.GPIO.setwarnings(False)
		self.modele = 'RPi'
		self.revision = RPi.GPIO.RPI_REVISION 	# n° de version du rpi
											#	1 = Rev 1
											#	2 = Rev 2
											#	3 = Model B+/A+
		self.pin={}
		#	self.pin[physical_no] = digital_rpi_pin_io(physical_no, wPi_no, BCM_no)
		if self.revision == 1:
			self.pin[3]=digital_rpi_pin_io(3,8,0)		# GPIO.00	SDA.0	(i2c)
			self.pin[5]=digital_rpi_pin_io(5,9,1)		# GPIO.01	SCL.0	(i2c)
			self.pin[13]=digital_rpi_pin_io(13,2,21)	# GPIO.21	SPI0_SCLK
		else:	#pour Modele B2 and next
			self.pin[3]=digital_rpi_pin_io(3,8,2)		# GPIO.02	SDA.1	(i2c)
			self.pin[5]=digital_rpi_pin_io(5,9,3)		# GPIO.03	SCL.1	(i2c)
			self.pin[13]=digital_rpi_pin_io(13,2,27)	# GPIO.27
		self.pin[7]=digital_rpi_pin_io(7,7,4)			# GPIO.04	GPCLK0
		self.pin[8]=digital_rpi_pin_io(8,15,14)			# GPIO.14
		self.pin[10]=digital_rpi_pin_io(10,16,15)		# GPIO.15
		self.pin[11]=digital_rpi_pin_io(11,0,17)		# GPIO.17
		self.pin[12]=digital_rpi_pin_io(12,1,18)		# GPIO.18	PMC_CLK
		self.pin[15]=digital_rpi_pin_io(15,3,22)		# GPIO.22
		self.pin[16]=digital_rpi_pin_io(16,4,23)		# GPIO.23
		self.pin[18]=digital_rpi_pin_io(18,5,24)		# GPIO.24
		self.pin[19]=digital_rpi_pin_io(19,12,10)		# GPIO.10	SPI0_MOSI
		self.pin[21]=digital_rpi_pin_io(21,13,9)		# GPIO.9	SPI0_MISO
		self.pin[22]=digital_rpi_pin_io(22,6,25)		# GPIO.25
		self.pin[23]=digital_rpi_pin_io(23,14,11)		# GPIO.11	SPI0_SCLK
		self.pin[24]=digital_rpi_pin_io(24,10,8)		# GPIO.8	SPI0_CEO_N
		self.pin[26]=digital_rpi_pin_io(26,11,7)		# GPIO.7	SPI0_CE1_N

		if self.revision == 3:	#Raspberry 2 and B+
			self.pin[27]=digital_rpi_pin_io(27,30,0)	# SDA.0
			self.pin[28]=digital_rpi_pin_io(28,31,1)	# SCL.0
			self.pin[29]=digital_rpi_pin_io(29,21,5)	# GPIO.5
			self.pin[31]=digital_rpi_pin_io(31,22,6)	# GPIO.6
			self.pin[32]=digital_rpi_pin_io(32,26,12)	# GPIO.12
			self.pin[33]=digital_rpi_pin_io(33,23,13)	# GPIO.13
			self.pin[35]=digital_rpi_pin_io(35,24,19)	# GPIO.19
			self.pin[36]=digital_rpi_pin_io(36,27,16)	# GPIO.16
			self.pin[37]=digital_rpi_pin_io(37,25,26)	# GPIO.26
			self.pin[38]=digital_rpi_pin_io(38,28,20)	# GPIO.20
			self.pin[40]=digital_rpi_pin_io(40,29,21)	# GPIO.21



	def bcm_pin(self, no_pin):
		''' Renvoie la pin_io nommés par son n° BMC
		'''
		for pin in self.pin.values():
			if pin.bcm_id==no_pin:
				return pin

	def bcm_pins(self, *no_pins):
		''' Renvoie la liste des pins nommés par les n° BCM
		'''
		pins = []
		for no_pin in no_pins:
			for pin in self.pin.values():
				if no_pin == pin.bcm_id:
					pins.append(pin)
		return pins
