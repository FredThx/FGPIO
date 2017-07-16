#!/usr/bin/env python
# -*- coding:utf-8 -*


'''
 Utilisation de MPU-6050 (Invensense )
	Gyroscope 3 axes
	Acceleromètre 3 axes

 AUTEUR : FredThx

 Projet : rpiduino_io

'''
from i2c_device_io import *
import math

class mpu_6050_io(i2c_device_io):
	''' a MPU-6050 gyroscope and accelerometre
	'''
	power_mgmt_1 = 0x6b
	power_mgmt_2 = 0x6c
	gyro_xout_adr = 0x43
	gyro_yout_adr = 0x45
	gyro_zout_adr = 0x47
	gyro_scale = 131.0
	accel_xout_adr = 0x3b
	accel_yout_adr = 0x3d
	accel_zout_adr = 0x3f
	accel_scale = 16384.0
	
	def __init__(self,bus=None, addr=0x68, pc = None):
		'''Initialisation
			bus : n° du bus (defaut 1 pour RPi et 2 pour pcduino (mais il faut préciser pc))
			addr = adresse i2c de l'écran ( pour detecter : i2cdetect -y no_bus)
			pc : rpiduino_io
		'''
		i2c_device_io.__init__(self, bus, addr, pc)
		self.device.write_cmd_arg(self.power_mgmt_1,0)	#Wake up the device
	
	def _read_word_2c(self, adr):
		high = self.device.read_data(adr)
		low = self.device.read_data(adr+1)
		val = (high << 8) + low
		if (val >= 0x8000):
			return -((65535 - val) + 1)
		else:
			return val
	
	def get_gyro(self):
		'''Renvoie un tuple avec les 3 valeurs du gyroscope
			(gyro_xout, gyro_yout, gyro_zout)
		'''
		gyro_xout = self._read_word_2c(self.gyro_xout_adr)/self.gyro_scale
		gyro_yout = self._read_word_2c(self.gyro_yout_adr)/self.gyro_scale
		gyro_zout = self._read_word_2c(self.gyro_zout_adr)/self.gyro_scale
		return (gyro_xout, gyro_yout, gyro_zout)
	
	def get_accel(self):
		'''Renvoie un tuple avec les 3 valeurs de l'acceléromètre
			(accel_xout, accel_yout, accel_zout)
		'''
		accel_xout = self._read_word_2c(self.accel_xout_adr)/self.accel_scale
		accel_yout = self._read_word_2c(self.accel_yout_adr)/self.accel_scale
		accel_zout = self._read_word_2c(self.accel_zout_adr)/self.accel_scale
		return (accel_xout, accel_yout, accel_zout)
	
	@staticmethod
	def _dist(a,b):
		return math.sqrt((a*a)+(b*b))
	
	def get_xy_rotation(self):
		'''Renvoie les composantes x,y de la position angulaire
		'''
		(accel_x, accel_y, accel_z) = self.get_accel()
		angle_x = math.atan2(accel_y, self._dist(accel_x, accel_z))
		angle_y = math.atan2(accel_x, self._dist(accel_y, accel_z))
		return (math.degrees(angle_x), math.degrees(angle_y))
	

#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################

if __name__ == '__main__':
	from rpiduino_io import *
	pc = rpiduino_io()
	mpu6050 = mpu_6050_io(pc=pc)
	while True:
		(gyro_x, gyro_y, gyro_z) = mpu6050.get_gyro()
		(accel_x, accel_y, accel_z) = mpu6050.get_accel()
		print 'Gyroscope :'
		print '     : x=%s' % gyro_x
		print '     : y=%s' % gyro_y
		print '     : z=%s' % gyro_z
		print 'Accelerometre :'
		print '     : x=%s' % accel_x
		print '     : y=%s' % accel_y
		print '     : z=%s' % accel_z
		time.sleep(0.1)
		