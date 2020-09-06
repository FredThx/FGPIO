#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
 Utilisation d'un bouton rotatif à 5 pins
	ex : http://www.adafruit.com/products/377

	Classe : 	- bt_rotatif_io			:	vrai bouton rotatif
				- bt_pseudo_rotatif_io	:	simulation avec 3 boutons poussoirs

 AUTEUR : FredThx

 Projet : rpiduino_io

'''


from rpiduino_io import *
from bt_io import *

class bt_rot_io(digital_input_device_io):
	''' Bouton rotatif
			Soit réel	:	bt_rotatif_io
			Soit pseudo	:	bt_pseudo_rotatif_io
	'''
	def __init__(self, pin_sw=None, value = 0, min_value = None, max_value = None, \
				sw_thread = False, on_sw_changed = None, sw_pause = 0.1, \
				rot_thread = False, on_rot_changed = None, rot_pause = 0.1):
		'''Initialisation
			- pin_sw		:	pin pour intérupteur (facultatif)
			- value	 		:	valeur initiale (pour comptage)
			- min_value		:	valeur minimum
			- max_value		:	valeur maximale
			- sw_thread		:	True/False : deamon sur le bouton poussoir
			- on_sw_changed	:	fonction a executer quand l'état du bouton est changé
			- sw_pause		:	pause entre chaque lecture le l'état du bouton
			- rot_thread	:	True/False/'auto' : deamon sur la rotation
								si 'auto' : création d'un deamon automatique qui va gérer value
			- on_rot_changed:	fonction a executer quand le bouton est tourné
			- rot_pause		:	pause entre chaque lecture le l'état du bouton
			- auto			:	gestion optimiser de la lecture par thread
		'''
		if pin_sw != None:
			self.sw = bt_io(pin_sw, sw_thread, on_sw_changed, sw_pause)
		self.value = value
		self.max_value = max_value
		self.min_value = min_value
		if rot_thread == 'auto':
			self.on_rot_changed = on_rot_changed
			digital_input_device_io.__init__(self, True, self.auto_on_rot_changed, rot_pause)
		else:
			digital_input_device_io.__init__(self, rot_thread, on_rot_changed, rot_pause)

	def read_value(self):	#Obsolete
		""" renvoie la valeur cumulée
				pour initialiser : self.value = 0
		"""
		self.value += self.read()
		return self.value

	def set_value(self, value):
		self.value = value
		if self.min_value!=None:
			if self.value < self.min_value:
				self.value = self.min_value
		if self.max_value!=None:
			if self.value > self.max_value:
				self.value = self.max_value

	def auto_on_rot_changed(self):
		''' Deamon pour lecture automatique de la rotation
			et incrémentation/decrémentation value
		'''
		if self.th_readed()!=0:
			self.set_value(self.value + self.th_readed())
			if self.on_rot_changed:
				self.on_rot_changed()

	@property
	def is_pressed(self):
		''' renvoie True si le bouton est pressé. False sinon
		'''
		return self.sw.is_pressed

	def is_pushed(self):
		''' renvoie true si le bouton devient appuyé
			(s'il reste appuyé, renvoie False)
		'''
		return self.sw.is_pushed()

	def stop(self):
		self.sw.stop()
		input_device_io.stop(self)

	def add_thread(self, on_sw_changed = None, sw_pause = 0.1, \
						rot_thread = True, on_rot_changed = None, rot_pause = 0.1):
		'''Ajoute le mécanisme de thread a un composant qui n'en a pas
			- on_sw_changed	:	fonction a executer quand l'état du bouton est changé
			- sw_pause		:	pause entre chaque lecture le l'état du bouton
			- rot_thread	:	True/False/'auto' : deamon sur la rotation
								si 'auto' : création d'un deamon automatique qui va gérer value
			- on_rot_changed:	fonction a executer quand le bouton est tourné
			- rot_pause		:	pause entre chaque lecture le l'état du bouton
		'''
		if on_sw_changed != None:
			assert (not self.sw.thread), ' bt_rot_io has already a thread on switch changed'
			input_device_io.__init__(self.sw, True, on_sw_changed, None, sw_pause)
		if rot_thread == 'auto':
			assert (not self.thread), 'bt_rot_io has already a thread on rotary'
			self.on_rot_changed = on_rot_changed
			digital_input_device_io.__init__(self, True, self.auto_on_rot_changed, None, rot_pause)
		else:
			assert (not self.thread), 'bt_rot_io has already a thread on rotary'
			input_device_io.__init__(self, True, on_rot_changed, None, rot_pause)

class bt_rotatif_io(bt_rot_io):
	''' Bouton rotatif à 5 pins
		Branchements :
			d'un coté :
				- 0 V
				- pin_sw
			de l'autre :
				- pin_a
				- 0 V
				- pin_b
	'''
	def __init__(self, pin_a, pin_b, pin_sw=None, value = 0, min_value = None, max_value = None, \
				sw_thread = False, on_sw_changed = None, sw_pause = 0.1, \
				rot_thread = False, on_rot_changed = None, rot_pause = 0.1, \
				auto = False):
		'''Initialisation
			- pin_a			:	pin pour rotation
			- pin_b			:	pin pour rotation
			- pin_sw		:	pin pour intérupteur (facultatif)
			- value	 		:	valeur initiale (pour comptage)
			- min_value		:	valeur minimum
			- max_value		:	valeur maximale
			- sw_thread		:	True/False : deamon sur le bouton poussoir
			- on_sw_changed	:	fonction a executer quand l'état du bouton est changé
			- sw_pause		:	pause entre chaque lecture le l'état du bouton
			- rot_thread	:	True/False/'auto' : deamon sur la rotation
								si 'auto' : création d'un deamon automatique qui va gérer value
			- on_rot_changed:	fonction a executer quand le bouton est tourné
			- rot_pause		:	pause entre chaque lecture le l'état du bouton
			- auto			:	gestion optimiser de la lecture par thread
		'''
		self.pin_a = pin_a
		self.pin_b = pin_b
		self.pin_a.setmode(PULLUP)
		self.pin_b.setmode(PULLUP)
		self.auto = auto
		# Si mode automatique
		if self.auto:
			self.auto_thread = f_thread(self._auto_read)
			self.lasts_read = [0,0,0]
			self.auto_reads=[]
			self.auto_thread.start()
		else:
			self.lasts_read = [0,0,0,0]

		bt_rot_io.__init__(self, pin_sw, value, min_value, max_value, \
							sw_thread, on_sw_changed, sw_pause, \
							rot_thread, on_rot_changed, rot_pause)

	# Quand on tourne d'un cran,
	#	Clockwise :	pin_a	pin_b	value
	#				1		0		0b10 (environ 0.015 secondes)
	#				0		0		0b00 (environ 0.005 secondes)
	#				0		1		0b01 (environ 0.005 secondes)
	#				1		1		0b11 (attente)
	#	trigo :
	#				0		1		0b01(environ 0.015 secondes)
	#				0		0		0b00(environ 0.005 secondes)
	#				1		0		0b10(environ 0.005 secondes)
	#				1		1		0b11 (attente)
	# sauf que le bouton peut rester coincer sur autre chose de 0b11!!!

	def _read(self):
		return self.pin_a.get() | self.pin_b.get()<<1

	def _basic_read(self):
		value = self._read()
		if self.lasts_read[3]==value:
			return 0
		else:
			self.lasts_read.append(value)
			del self.lasts_read[0]
			if self.lasts_read==[0b10,0b00,0b01,0b11]:
				return -1
			elif self.lasts_read==[0b01,0b00,0b10,0b11]:
				return 1
			else:
				return 0

	def read(self):
		''' Renvoie
			+1 si le bouton est tourné à droite
			-1 si le bouton est tourné à gauche
			0 sinon
		'''
		if self.auto:
			return self._read_auto_read()
		else:
			return self._basic_read()

	def _read_auto_read(self):
		# Renvoie la première valeur dans auto_reads et la supprime
		if self.auto_reads:
			value = self.auto_reads[0]
			del self.auto_reads[0]
			return value
		else:
			return 0

	def _auto_read(self):
		#Lecture en continue des pins
		#et remplissage de self.auto_reads
		value = self._read()
		if self._read()!=0b11:
			if self.lasts_read[2]!=value:
				self.lasts_read.append(value)
				del self.lasts_read[0]
				if self.lasts_read==[0b10,0b00,0b01]:
					self.auto_reads.append(-1)
				elif self.lasts_read==[0b01,0b00,0b10]:
					self.auto_reads.append(1)
			time.sleep(0.002)
		else:
			time.sleep(0.015)

	def stop(self):
		if self.auto:
			self.auto_thread.stop()
		bt_rot_io.stop(self)

class bt_pseudo_rotatif_io(bt_rot_io):
	""" Pseudo bouton rotatif
			simulé à partir de 3 boutons poussoirs
	"""
	def __init__(self, pin_plus, pin_moins, pin_sw = None, value = 0, min_value = None, max_value = None, \
				sw_thread = False, on_sw_changed = None, sw_pause = 0.1, \
				rot_thread = False, on_rot_changed = None, rot_pause = 0.1):
		"""Initialisation
				- pin_plus	:	pin_io du bouton poussoir +
				- pin_moins	:	pin_io du bouton poussoir -
				- pin_sw 	:	pin_io du bouton de validation (facultatif)
		"""
		self.bt_plus = bt_io(pin_plus)
		self.bt_moins = bt_io(pin_moins)
		bt_rot_io.__init__(self, pin_sw, value, min_value, max_value, \
							sw_thread, on_sw_changed, sw_pause, \
							rot_thread, on_rot_changed, rot_pause)

	def read(self):
		""" Renvoie
			+1 si le bouton plus est appuyé
			-1 si le bouton moins est appuyé
			0 si aucun ou les deux sont appuyés
		"""
		value = 0
		if self.bt_plus.is_pushed():
			value+=1
		if self.bt_moins.is_pushed():
			value-=1
		return value




#########################################################
#                                                       #
#		EXEMPLEs                                        #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()

	#################################
	#								#
	#	Exemple Idéal				#
	#								#
	#################################

	bt = bt_rotatif_io(*pc.logical_pins(9,10,8), auto=True)
	print("Appuyer sur le bouton")
	while not bt.is_pushed():
		time.sleep(0.1)
	print("Tourner maintenant")
	while not bt.is_pushed():
		value = bt.read()
		if value==1:
			print('up')
		elif value==-1:
			print('down')
		time.sleep(0.1)
	print("Ok.")

	bt.stop()
	raise ValueError

	#################################
	#								#
	#	Exemple Basique				#
	#								#
	#################################

	bt = bt_rotatif_io(*pc.logical_pins(9,10,8))
	#bt = bt_pseudo_rotatif_io(*pc.logical_pins(9,10,8))
	print("Appuyer sur le bouton")
	while not bt.is_pushed():
		pass
	print("Tourner maintenant")
	while not bt.is_pushed():
		print(bt.read_value())
	print("Ok.")

	#################################
	#								#
	#	Exemple avec deux threads	#
	#								#
	#################################

	def on_push_action():
		if bt.sw.th_readed():
			print('pushed')
			bt.stop()
	def on_rot_action():
		if bt.th_readed() == 1:
			print('up')
		if bt.th_readed() == -1:
			print('down')
	print('Utilisation de deux thread (push pour stopper)')
	bt = bt_rotatif_io(*pc.logical_pins(9,10,8), \
				sw_thread = True, on_sw_changed = on_push_action, \
				rot_thread = True, on_rot_changed = on_rot_action )

	while not bt.thread.terminated:
		time.sleep(1)

	#################################
	#								#
	#	Exemple mode auto			#
	#								#
	#################################

	print('Utilisation du bouton en automatique')
	print('A 5, on stoppe')
	def on_push_action2():
		if bt.sw.th_readed():
			print(bt.value)
		if bt.value>5:
			bt.stop()


	bt = bt_rotatif_io(*pc.logical_pins(9,10,8), \
				sw_thread = True, on_sw_changed = on_push_action2, \
				rot_thread = 'auto', on_rot_changed = None )

	while not bt.thread.terminated:
		time.sleep(1)

	#################################
	#								#
	#	Exemple mode auto + deamon	#
	#								#
	#################################

	print('Utilisation du bouton en mode auto + deamon')

	from lcd_i2c_io import *
	lcd = lcd_i2c_io(pc=pc)
	lcd.message('X',1)
	lcd.message('push pour quitter',2)

	def on_value_change():
		lcd.message('X'.rjust(bt.value),1)

	def on_push_action3():
		bt.stop()

	bt = bt_rotatif_io(*pc.logical_pins(9,10,8), \
				sw_thread = True, on_sw_changed = on_push_action3, \
				rot_thread = 'auto', on_rot_changed = on_value_change, \
				value = 1, max_value = 16, min_value = 1)
	while not bt.thread.terminated:
		time.sleep(1)
	lcd.clear()
	# try: #Ca permet de pouvoir planter le thread avec un CTRL-C
		# while True:
			# time.sleep(1)
	# except KeyboardInterrupt:
		# bt.stop()
