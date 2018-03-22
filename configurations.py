#!/usr/bin/env python

__doc__ = \
'''
'''

__version__ = '0.1'

__authors__ = [
				"Version 0.1: Joao Pio <pio.joao@gmail.com>"
			]

#Standard packages
import os
import json
import re
from schema import SchemaError
from schema import Schema, And, Use, Optional, Regex

class Configurations():
	
	#Class Constructor
	def __init__(self):

		self.schema = Schema(
		{
			'gmail':
				{
				'username': Use(str),
				'password' : Use(str),
				'attachmentsPath' : Regex(r'^/.*$'),
				'allowedSubjects' :[Use(str)],
				'allowedImageFormats' :[Use(str)],
				'allowedVideoFormats' :[Use(str)],
				'blacklist' : Use(dict)
				},
			'instagram':
				{
				'username': Use(str),
				'password' : Use(str),
				'access_token' : Use(str),
				'client_secret' : Use(str),
				'user_id': Use(str)
				}
		})
		
		#Total configurations
		self.confs = None
		#Sub configurations
		self.gmail = None
		self.instagram = None

	#Loads the configuration file to a dictionary
	def load_configurations(self, file):

		#load the configuration file
		self.confs = json.load(file)
		
		#Validate the configurations
		self.schema.validate(self.confs)
		
		#copy the subconfs
		self.gmail = self.confs["gmail"]
		self.instagram = self.confs["instagram"]
			

		
		