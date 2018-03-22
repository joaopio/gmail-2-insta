#!/usr/bin/env python

__doc__ = \
'''
'''

__version__ = '0.1'

__authors__ = [
				"Version 0.1: Joao Pio <joao-t-pio@telecom.pt>"
			]

import logging

class G2ILogger():
	
	#Class Constructor
	def __init__(self, loglevel=logging.INFO):
		
		#Logging formats
		self.FORMAT_CLEAN = "%(levelname)7s: %(message)s"
		self.FORMAT_MIDDLE = "%(levelname)7s: %(funcName)20s() - %(message)s"
		self.FORMAT_DETAILED = "[%(filename)10s:%(lineno)4s - %(funcName)15s()] 	%(levelname)7s: %(message)s"
		
		#Logging definition
		self.log = logging.getLogger('NamfLogger')
		self.log_handler = logging.StreamHandler()  # Handler for the logger
		self.log_handler.setFormatter(logging.Formatter(self.FORMAT_CLEAN))
		self.log.addHandler(self.log_handler)
		self.log.setLevel(loglevel)
		

	def set_format(self, format="%(levelname)8s: %(message)s"):

		#Set the format
		self.log_handler.setFormatter(logging.Formatter(format))

	def set_level(self, level):
		
		#Set warning level
		self.log.setLevel(level)
		
logger = G2ILogger()
