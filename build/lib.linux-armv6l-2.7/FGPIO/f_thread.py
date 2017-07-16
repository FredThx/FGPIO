#!/usr/bin/env python
# -*- coding:utf-8 -*


"""
	Une petite classe de Thread
		basée sur threading
		ou l'on passe une fonction en arguments
		
		usage : mon_thread = f_thread(ma_fonction, arg1, arg2, ..., nom_arg = arg, ...)
				mon_thread.start()
"""

import threading
import logging
import sys


class f_thread(threading.Thread):
	''' Classe de thread
	'''
	def __init__(self, fonction, *args, **kwargs):
		"""Initialisation
				- fonction		:	une fonction
				- args, kwargs	:	ses arguments
		"""
		threading.Thread.__init__(self)
		self.fonction = fonction
		self.args = args
		self.kwargs = kwargs
		self.terminated = False
		
	def run(self):
		'''Running the fonction of the thread
		'''
		logging.info('f_thread ' + self.fonction.__name__ + ' started.')
		loops = 0
		while not self.terminated:
			try:
				self.fonction(*self.args, **self.kwargs)
				loops += 1
			except:
				sys.excepthook(*sys.exc_info()) #Pour que les exceptions soient bien gérées par le module my_logging
				raise
		logging.info(self.fonction.__name__ + ' stopped after %s loops' % loops)
	
	def stop(self):
		'''Stop the thread at the next loop of the thread fonction.
		'''
		logging.info("Send terminated order to %s" % self)
		self.terminated = True

class f_thread_noerror(f_thread):
	''' f_thread with no error run fonction
	'''
	def run(self):
		'''Running fonction of the thread witch never died
		'''
		logging.info('f_thread ' + self.fonction.__name__ + ' started.')
		loops = 0
		while not self.terminated:
			try:
				self.fonction(*self.args, **self.kwargs)
				loops += 1
			except Exception, e:
				logging.error("Unexpected error in thread %s : %s"% (self.fonction, e))
		logging.info(self.fonction.__name__ + ' stopped after %s loops' % loops)


#########################################################
#                                                       #
#		EXEMPLE                                         #
#                                                       #
#########################################################


if __name__ == '__main__':
	import time
	def f1(a):
		print a
	def f2():
		print 'f2'
	def f3():
		print 'f3'
		
	th_f1 = f_thread(f1,"f1")
	th_f2 = f_thread(f2)
	th_f3 = f_thread(f3)

	th_f1.start()
	th_f2.start()
	th_f3.start()

	# Pour pouvoir planter le programme en ctrl-c
	try:
		while True:
			time.sleep(2)
	except KeyboardInterrupt:
		th_f1.stop()
		th_f2.stop()
		th_f3.stop()