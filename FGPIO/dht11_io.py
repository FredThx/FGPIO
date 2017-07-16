#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
DHT11 temperature and humidity sensor
 
	wiring :	pin 1	:	3.3V (or 5V)
				pin 2	:	data : a digital pin
				pin 3	:	n/ab
				pin 4	:	0V
				
	Note : 	Can only be used on RPi.
			pcduino GPIO usage is too slow
				
 AUTHOR : FredThx

 Project : rpiduino_io

'''

import time
import logging
from rpiduino_io import *
#TODO : rendre le _read() implantable

class dht11_io(multi_digital_input_device_io):
	''' a DHT11 temperature and humiditu sensor
	'''
	wake_up_delay = 0.014
	
	def __init__(self, pin_data, timeout_read = 4, thread = False, on_changed = None, discard = None, pause = 1, timeout = 30):
		'''Initialisation
				- pin_data		:	digital_pin_io
				- timeout_read	:	timeout for reading sensor
				- thread		:	(facultatif) True si utilisation thread
				- on_changed	:	fonction ou string executable
									qui sera lancée quand la valeur du capteur change
				- discard		:	ecart en dessous duquel une valeur est considérée comme inchangée
										a tuple of values in the same order than mesures
										or a dict ex {'T': discard_for_T, 'RH': discard_for_RH}
				- pause 		:	pause entre chaque lecture du composant
				- timeout		:	durée après laquelle une valeur lue est obsolète
		'''
		assert isinstance(pin_data, digital_rpi_pin_io), "pin_data must be a digital_rpi_pin_io."
		self.pin_data = pin_data
		self.nbdatas = 5000
		self.timeout_read = timeout_read
		# Initialize the nbdatas needed
		self.nbdatas = int((self.nbdatas - self._read_raw()[-1][1] )*1.2)
		# Test si discard est un Dico
		if isinstance(discard, dict):
			for cle in discard:
				assert cle in ('T', 'RH'), 'discard error : bad key'
		multi_digital_input_device_io.__init__(self, ('T', 'RH'), thread, on_changed, discard, pause, timeout)
		logging.info("dht11_io id created on pin %s." % self.pin_data)
	
	def _read_raw(self):
		datas = []
		bcm_no_pin = self.pin_data.bcm_id
		
		# Wake up the device
		self.pin_data.setmode(OUTPUT)
		RPi.GPIO.output(bcm_no_pin, RPi.GPIO.HIGH)
		time.sleep(2*dht11_io.wake_up_delay)
		RPi.GPIO.output(bcm_no_pin, RPi.GPIO.LOW)
		time.sleep(dht11_io.wake_up_delay)
		
		# Store the response of the device
		RPi.GPIO.setup(bcm_no_pin, RPi.GPIO.IN, RPi.GPIO.PUD_UP)
		i=0
		while i<self.nbdatas:
			datas.append(RPi.GPIO.input(bcm_no_pin))	#Direct usage of RPi.GPIO functions to increase speed of read
			i+=1
		
		#Analyse the datas
		count = 0
		tmp = datas[0]
		f_datas = []
		for data in datas:
			if data == tmp:
				count += 1
			else :
				f_datas.append((tmp, count))
				count = 1
				tmp = data
		f_datas.append((datas[-1], count))
		return f_datas[2:] # two first 0 - 1  are not datas
		
	def _read(self):
		'''Lecture du capteur par
				- Reveil du capteur : 
					- envoie de 18ms de LOW
					- envoie de 40µs de HIGH
				- Reponse au reiveil :
					- 80 µs à LOW
					- 80 µs à HIGH
				- lecture trame datas
			Return a dictionary : {'T': Temperature as int ,'RH' : Humidity as int}
		'''
		f_datas = self._read_raw()
		#S'il n'y a pas assez de données, on en rajoute.
		while f_datas[-1][1] < 100:
			self.nbdatas = int(self.nbdatas * 1.1)
			f_datas = self._read()
		logging.debug(f_datas)
		#Calcul du 'temps' moyen des passages à LOW
		count = 0
		sum = 0
		for f_data in f_datas:
			if f_data[0] == 0:
				count += 1
				sum += f_data[1]
		assert count > 0, 'Sensor does not respond'
		pulse = sum / count
		logging.debug("pulse = " + pulse)
		#Extraction des données binaires
		bits = ""
		for f_data in f_datas:
			if f_data[0] == 1:
				if f_data[1] < pulse:
					bits+="0"
				else:
					bits+="1"
		bits = bits[:-1]
		logging.debug(bits + " " + len(bits))
		# Calcul des valeurs
		assert len(bits)==40, 'Data Size error'
		RH = int(bits[:8],2)
		T = int(bits[16:24],2)
		CRC = int(bits[32:40],2)
		# Make CRC test
		assert CRC == RH + T, "CRC Error"
		
		return {'T': T, 'RH': RH}
	
	def read(self):
		'''read the sensor and
			Return a dictionary : {'T': Temperature as int ,'RH' : Humidity as int}
		'''
		timeout = time.time() + self.timeout_read
		reponse = False
		while time.time() < timeout and reponse == False:
			try:
				reponse =  self._read()
			except AssertionError:
				reponse = False
				time.sleep(1)
		return reponse

class dht11Error(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return self.message		


#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	pc = rpiduino_io()
	capteur = dht11_io(*pc.bcm_pins(23))
	reponse = capteur.read()
	if reponse:
		print "La température est de %s °C. L'humidité est de %s" % (reponse['T'], reponse['RH']), '%.'
	else:
		print "Sensor Error"
	#usage of thread
	def action():
		if capteur.th_readed():
			print "La température est de %s °C. L'humidité est de %s" % \
				(capteur.th_readed_value('T'), capteur.th_readed_value('RH')), '%.'
	
	capteur = dht11_io(*pc.bcm_pins(23), thread = True, \
						on_changed = action, discard = {'RH':2})
	
	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		capteur.stop()