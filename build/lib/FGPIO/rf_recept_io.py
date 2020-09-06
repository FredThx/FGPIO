#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# Recepteur Radio Fréquence (433Mhz)
# lié à un emetteur RF géré par arduino
# (ou directement ATMEGA328)
#
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''
####################################

import time
from collections import Counter
from rpiduino_io import *
import logging


#TODO : utiliser la méthode PulseIn de la class pin_io

class rf_recept_io:
	'''Recepteur Radio Fréquence
	'''
	low_pulse = 1000	# Duration (ms) of a low pulse
	high_pulse = 2500	# Duration (ms) of a high pulse

	def __init__(self, pin):
		'''Initialisation
			-pin		pin_io	pin data du recepteur RF
		'''
		self.pin = pin
		self.pin.setmode(INPUT)
		logging.info('re_recept_io created attached on %s' % self.pin)

	def pulseIn(self, timeout = 1):
		'''Lecture d'une pulsation
			Renvoie la durée de la pulsation (temps à LOW)
		'''
		timeout = time.time() + timeout
		while self.pin.get()==HIGH:
			if time.time() > timeout:
				return None
		now = time.time()
		while self.pin.get()==LOW:
			if time.time() > timeout:
				return None
		duree = time.time()-now
		return int(duree*1000000)

	def _get_one_bit(self):
		'''Lecture d'une pulsation sous forme de bit.
		'''
		t=self.pulseIn()
		if t:
			if self.high_pulse * 1.3 > t >= self.high_pulse * 0.75:
				return 1
			elif self.low_pulse * 1.3 > t > self.low_pulse * 0.75:
				return 0
			else:
				return None
		else:
			return None

	def get_bit(self):
		'''Renvoie un bit de données
			Décodage pulsations par code Manchester
		'''
		b1 = self._get_one_bit()
		b2 = self._get_one_bit()
		if b1==0 and b2==1:
			return 0
		elif b1==1 and b2==0:
			return 1
		else:
			return None

	@staticmethod
	def decode_manchester(datas, partial = False):
		'''Decode the Manchester code
			Return None if error
		'''
		if len(datas)%2==0:
			result = []
			for i in range(len(datas)/2):
				if datas[2*i]==0 and datas[2*i+1]==1:
					result.append(0)
				elif datas[2*i]==1 and datas[2*i+1]==0:
					result.append(1)
				else:
					if partial:
						return result
					else:
						return None
			return result
		else:
			return None

class temperature_rf_recept_io(rf_recept_io, multi_digital_input_device_io):
	'''Recepteur de températures RF
		Les sondes sont gérées par ATMEGA328 (programme maison)
	'''
	def __init__(self, pin, nb_bits_data = 11, signed = True, nb_bits_device = 4, \
			thread = False, on_changed = None, discard = None, pause = 0.1, timeout = 10):
		'''Initialisation
			- pin				pin_io, pin of RF recept
			- nb_bits_data		lenght of datas
			- signed			True if the last bit of datas is the signe
			- nb_bits_device	lenght of the device identification
		'''
		rf_recept_io.__init__(self, pin)
		self.nb_bits_data = nb_bits_data
		self.signed = signed
		self.nb_bits_device = nb_bits_device
		self.sensors = {}
		multi_digital_input_device_io.__init__(self, (), thread, on_changed, discard, pause, timeout)

	def add_sensor(self, id_sensor, name= None):
		'''Add a sensor in the sensors dict
			- id_sensor		code identification (ex : '1001')
			- name			name of the sensor
		'''
		if name == None:
			name = 'Temp_' + id_sensor
		self.sensors[id_sensor]=name
		assert [k for k,v in Counter(self.sensors.values()).items() if v>1]==[], \
			'temperature_rf_recept_io : sensor name must be unique'
		self.mesures = tuple(self.sensors.values())

	def wait_for_init(self):
		'''Wait for the init signal:
			             __               _
			               |_____________| |_______|
		duration (ms)	 275   9900      275  2675
		'''
		t = 0
		while t < 9000 or t > 11000:
			t = self.pulseIn()
			time.sleep(0.0002)
		while t < 2300 or t > 3000:
			t = self.pulseIn()

	def read_one(self):
		'''Lecture de la mesure
			- signal de début
			- 10 bits pour la valeur mesurée
			- 1 bit pour le signe (0=négatif)
			- 4 bits pour l'identification du capteur
			Chaque bit étant codé en Manchester
				- [0,1] => 0
				- [1,0] => 1
		'''
		self.wait_for_init()
		datas=[]
		#Lecture de toutes les valeurs
		#Pour plus d'efficatité, on fait la lecture en brute, le décodage se fera ensuite
		for i in range(30):
			datas.append(self._get_one_bit())
		#Décodage Manchester
		result = self.decode_manchester(datas)
		if result!=None:
			#Calcul décimal
			result_dec = self._list_to_int(result[:11])/10.
			capteur = ''.join([str(n) for n in result[11:]])
			return result_dec, capteur
		else:
			return None

	def populate(self, timeout = 30):
		'''Scan les capteurs RF et alimente self.sensors
		'''
		timeout = time.time() + timeout
		while time.time() < timeout:
			try:
				temp, id_sensor = self.read_one()
				logging.debug("Found sensor : %s. Value = %s"%(id_sensor, temp))
				self.add_sensor(id_sensor)
			except TypeError:
				pass
		return self.sensors

	def read(self, name = None, timeout = 30):
		''' Read all the sensors listed in self.sensors
			- name		(optionnal) name of the sensor
		'''
		if name == None:
			if self.sensors=={}:
				self.populate()
			timeout = time.time() + timeout
			sensors_readed={}
			while sensors_readed.keys() != self.sensors.keys() and time.time()<timeout:
				value_readed = self.read_one()
				if value_readed != None and value_readed[1] in self.sensors.keys():
					sensors_readed[value_readed[1]]=value_readed[0]
			result = {}
			for id in sensors_readed:
				result[self.sensors[id]]=sensors_readed[id]
			return result
		else:
			timeout = time.time() + timeout
			for id in self.sensors.keys():
				if self.sensors[id] == name:
					id_name = id
					break
			value = None
			while value == None and time.time()<timeout:
				value_readed = self.read_one()
				if value_readed != None and value_readed[1] == id_name:
					value = value_readed[0]
			return value

	@staticmethod
	def _list_to_int(bin_result):
		'''Transforme les données binaires sous forme de liste en entier
			Le dernier element de la liste représente le signe (0=négatif)
		'''
		result = 0
		n=len(bin_result)-2
		for i, val in enumerate(bin_result[:-1]):
			result += val*2**(n-i)
		if bin_result[-1]==0:
			result = - result
		return result



#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	pc = rpiduino_io()
	rf = temperature_rf_recept_io(pc.pin[40])
	#rf.populate(10)
	#print("Sensors found : ", rf.sensors)
	#print(rf.read())
	rf.add_sensor('0011', 'Bureau')
	rf.add_sensor('0010', 'Salon')
	print(rf.read())
	print('La température du Salon est de %s °C' % rf.read('Salon'))
	def action():
		if rf.th_readed():
			print("Changement de température!!!")
			print("La température du Salon est de %s °C. Celle du bureau est de %s °C." % \
				(rf.th_readed_value('Salon'), rf.th_readed_value('Bureau')))
	rf.add_thread(action, discard = 0.2)
	try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		rf.stop()
