#!/usr/bin/env python
# -*- coding:utf-8 -*

####################################
'''
# Un relay branchée sur un rpi_duino_io
# 
#    Nota : le relais est fermé ( à on ) quand la pin est à LOW
#			(et l'on veut que la led du relais corresponde à fermé)
# AUTEUR : FredThx
#
# Projet : rpiduino_io
#
'''


from on_off_output_device_io import *

#TODO : créer les méthodes
#		 	set_bt()
#			stop_bt()
#		pour affecter un bt au relai avec gestion par thread
#		(si jamais il y a une utilité!!!

class relay_io (on_off_output_device_io):
	''' Relay branché sur un rpiduino (pcduino ou Rpi)
	'''
	
	default_blink_time_on = 10
	
	def none_none(fonction):
		'''Décorateur : si pin==None : la fonction ne s'applique pas
		'''
		@functools.wraps(fonction) # ca sert pour avoir un help(SBClient) utile
		def none_none_fonction(self, *args, **kwargs):
			if self.pin == None:
				return None
			else:
				return fonction(self, *args, **kwargs)
		return none_none_fonction
	
	def set(self, etat):
		''' Ouvre ou ferme le relay
			- etat		:	True	: le relais est fermé
							False	: le relais est ouvert
		'''
		super(relay_io, self).set(not etat)
		
#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	import time
	pc = rpiduino_io()
	lampe = relay_io(pc.bcm_pin(25))
	none_dev = relay_io()
	print "Eteint"
	lampe.off()
	none_dev.on() # Do nothing!
	time.sleep(1)
	print "Allumé"
	lampe.on()
	time.sleep(1)
	print "Clignotant par defaut"
	lampe.blink()
	time.sleep(30)
	print "Clignotant 3 - 1"
	lampe.blink(3,1)	# Accelerate the blinking
	time.sleep(30)
	lampe.stop()		# Stop the blinking
	