#!/usr/bin/env python
# -*- coding:utf-8 -*

from FGPIO.dht11_io import *
from FGPIO.lcd_i2c_io import *

pc = rpiduino_io()
capteur = dht11_io(*pc.bcm_pins(23))

lcd = lcd_i2c_io(pc=pc)

reponse0 = ()
while True:
	reponse = capteur.read()
	if reponse:
		T = reponse['T']
		RH = reponse['RH']
		if reponse != reponse0:
			lcd.message("Temperat. : %s'C" % T, 1)
			lcd.message(("Humidite  : %s" % RH) + "%", 2)
			reponse0 = reponse
	time.sleep(5)