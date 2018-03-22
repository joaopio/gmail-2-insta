#!/usr/bin/env python

__doc__ = \
'''
	Extension of the "gmail" class from the gmail module obtained in:
		https://github.com/charlierguo/gmail
'''

__version__ = '0.1'

__authors__ = [
				"Version 0.1: Joao Pio <pio.joao@gmail.com>"
			]

#Default packages
from re import search as rsearch

#Third party packages
from gmail import Gmail

class GmailXT(Gmail):

	def getSenderAddress(self, mail):

		r = rsearch("<(.*?)>", mail.fr)

		if r:
			return r.group(1)

		return None


