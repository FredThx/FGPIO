#!/usr/bin/env python
# -*- coding:utf-8 -*


class vehicule(object):
	'''vehicule
	'''
	def __init__(self, vitesse=0, **kwargs):
		print("Init vehicule")
		self.vitesse = vitesse
	def roule(self):
		print("Je roule à %s km/h"%(self.vitesse))
	
class music_machine(object):
	''' Object qui fait de la musique
	'''
	def __init__(self, song = "Les fesses des belges", artist = "Les Wampas", **kwargs):
		print("Init music_machine")
		self.song = song
		self.artist = artist
	def play(self):
		'''
		play music
		'''
		print("Play %s - %s"%(self.song, self.artist))
		
	
class voiture(vehicule, music_machine):
	'''
	voiture
	'''
	def __init__(self, **kwargs):
		music_machine.__init__(self,**kwargs)
		vehicule.__init__(self,**kwargs)