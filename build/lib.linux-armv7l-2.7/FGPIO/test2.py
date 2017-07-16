#!/usr/bin/env python
# -*- coding:utf-8 -*

import time
from rpiduino_io import *
import RPi.GPIO as GPIO

pc = rpiduino_io()
if isinstance(pc, pcduino_io):
	input_pin = pc.pin[2]
if isinstance(pc, rpi_io):
	input_pin = pc.pin[26]
input_pin.setmode(INPUT)

data=[]
now = time.time()
for i in range(0,1000):
	data.append(GPIO.input(input_pin.physical_id))

print 'moyenne rpiduino_io: %i µs' % (1000*(time.time()-now))

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(26, GPIO.IN)

data=[]
now = time.time()
for i in range(0,1000):
    data.append(GPIO.input(26))

print 'moyenne RPi.GPIO : %i µs' % (1000*(time.time()-now))