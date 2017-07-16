#!/usr/bin/env python
# -*- coding:utf-8 -*


import RPi.GPIO as GPIO
import time,sys,getopt

from FGPIO.led_io import *


# Servo Control
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)
p = GPIO.PWM(7,50)
p.start(1)
time.sleep(1)
p.stop()
time.sleep(1)
p = GPIO.PWM(7,50)
p.start(4.5)
time.sleep(1)
p.stop()
p = GPIO.PWM(7,50)
p.start(10)
time.sleep(1)
p.stop()
p = GPIO.PWM(7,50)
p.start(2.75)
time.sleep(1)
p.stop()

delay_period=0.5
delay_period2=0.05

pos90=7.5
pos180=12.5
pos0=2.5

def action(statu):
	if statu == "fermeture":
		p.ChangeDutyCycle(2)
		time.sleep(delay_period)
		p.ChangeDutyCycle(7.5)
		time.sleep(delay_period2)
		print "Fermeture en cours"
	elif statu == "ouverture":
		print "Appui bouton haut..."
		p.ChangeDutyCycle(12.5)
		time.sleep(delay_period)
		p.ChangeDutyCycle(7.5)
		time.sleep(delay_period2)
		print "Ouverture en cours"
	else:
		print "ordre inconnu ou absent"
		print statu

