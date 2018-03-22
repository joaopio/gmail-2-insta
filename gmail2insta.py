#!/usr/bin/env python

__doc__ = \
'''
	
'''

__version__ = '0.1'

__authors__ = [
				"Version 0.1: Joao Pio <pio.joao@gmail.com>"
			]

#debug
import sys

#Standard packages
from os import path, remove
import json
import re
import argparse
from schema import SchemaMissingKeyError, SchemaError, SchemaUnexpectedTypeError
from schema import Schema, And, Use, Optional, Regex

#Third party APIs
#gmail==0.0.5
import gmail
from gmail.exceptions import GmailException, ConnectionError, AuthenticationError, Timeout
#InstagramAPI==1.0.2
from InstagramAPI import InstagramAPI
#Pillow==5.0.0
from PIL import Image
#moviepy==0.2.3.2
#required to circumvent InstagramAPI video upload bug. Only downloads the first time this script is executed
try:
	from moviepy.editor import VideoFileClip
except ImportError:
	import imageio
	imageio.plugins.ffmpeg.download()
	from moviepy.editor import VideoFileClip

#local packages
import configurations as cfg
from gmailExtended import GmailXT
from instaMedia import InstagramImage, InstagramVideo
from tools.g2ilog import logger

#Get the location of the python source file
PATH = path.dirname(path.abspath(__file__))

#arguments parser
def arg_parse():
	
	parser = argparse.ArgumentParser(description='Gmail to Instagram script.')
	
	parser.add_argument("--conf", default=path.join(PATH,"configurations.json"), type=argparse.FileType('r'), help='the configuration file')
	
	#Behaviour flags
	parser.add_argument("-v", "--verbose", action="store_true", default=False, help='increase output verbosity')
	parser.add_argument("-d", "--debug", action="store_true", default=False, help='increase output verbosity to debug mode')

	args = parser.parse_args()
	
	return args

def instagramConnect(configurations):

	logger.log.info("Attempting to log to instagram account")

	try:	
		ia = InstagramAPI(configurations.instagram["username"], configurations.instagram["password"])
	except Exception as e:
		logger.log.error("Could not initialize instagramAPI due to {0}".format(e))
		return

	try:
		#Double login to workaround Error 429 bug
		ia.login()
		ia.login()
	except Exception as e:
		logger.log.error("Could not login to instagram due to {0}".format(e))
		return

	if not ia:
		return False

	logger.log.info("Logged to Instagram")
	return ia

def main():

	#Parsing stage---------------------------------------------------------
	try:
		args = arg_parse()
	except Exception as e:
		logger.log.critical("Could not parse arguments due to {0}".format(e))
		return
	#----------------------------------------------------------------------


	#Configure logging according to args-----------------------------------
	if args.verbose:
		#change format and increase logging level
		logger.set_level(20)
		
	if args.debug:
		#change format and increase logging level
		logger.set_format(logger.FORMAT_MIDDLE)
		logger.set_level(10)
	#----------------------------------------------------------------------

	#Load configurations---------------------------------------------------
	try:
		configurations = cfg.Configurations()
		configurations.load_configurations(args.conf)
	except SchemaError as e:
		logger.log.critical("Could not validate configurations due to content not matching schema: {0}".format(e))
		return
	except ValueError as e:
		logger.log.critical("Could not validate configurations due to bad format of json file: {0}".format(e))
		return

	#Loading configurations failed
	if not configurations:
		logger.log.critical("Failed to load configurations. Aborting.")
		return
	#----------------------------------------------------------------------


	#Establish GMAIL connection-------------------------------------------------
	
	g = GmailXT() #gmail

	try:
		g.login(configurations.gmail["username"], configurations.gmail["password"])
	except AuthenticationError as e:
		logger.log.critical("Failed to logon to Gmail account due to {0}. Check username/password.".format(e))
		return

	unread_mails = None
	#----------------------------------------------------------------------

	#Email fetching and attachment downloading-----------------------------

	#attachment files list
	at_filelist = []

	#Iterate all allowed subjects
	for sub in configurations.gmail["allowedSubjects"]:

		#Get a list of emails that are unread and have subject as in the configurations file
		unread_mails = g.inbox().mail(unread=True, subject=sub)

		if len(unread_mails) != 0:

			logger.log.info("YOU GOT MAIL!")

			#Loop all the emails found
			for new_mail in unread_mails:
				
				#Fetch the email from the server
				new_mail.fetch()

				#Obtain the sender info from the header
				try:
					sender = g.getSenderAddress(new_mail)
				except Exception as e:
					logger.log.warning("Had trouble extracting sender info due to {0}. Moving on".format(e))

				#Sender was successfully extracted but is in the blacklist
				if sender and sender in configurations.gmail["blacklist"].keys():
					logger.log.info("{0} is blacklisted. Ignoring email.".format(sender))
					continue

				attachments = new_mail.attachments
				
				for attachment in attachments:
					logger.log.info("Saving attachment {0} with {1} Kbytes".format(attachment.name, attachment.size))
					
					attachment.save(configurations.gmail["attachmentsPath"])

					at_filelist.append(path.join(configurations.gmail["attachmentsPath"], attachment.name))

			#Mark email as read
			new_mail.read()

		else:
			logger.log.info("No new emails...")

	logger.log.info("Logging out of Gmail")
	g.logout()

	#----------------------------------------------------------------------

	#Process of downloaded images and videos-------------------------------

	#Lists of media treated for Instagram
	insta_img_list = []
	insta_video_list = []

	#If there were emails downloaded and they had attachments
	if unread_mails is not None and len(at_filelist) != 0:
		#Finished downloading all attachments. Proceed to processing and uploading the files
		for f2up in at_filelist:

			logger.log.info("Processing downloaded file {0}".format(f2up))

			#try to identify file based on file extension - IMAGES
			if path.splitext(f2up)[1] in configurations.gmail["allowedImageFormats"]:

				#Instantiate class and load the image in it
				insta_image = InstagramImage()
				try:
					insta_image.load(Image.open(f2up))
					insta_image.setCaption(new_mail.body)
				except TypeError as e:
					logger.log.warning("Could not load image due to {0}".format(e))
					continue
				except Exception as e:
					logger.log.warning("Could not load image due to {0}".format(e))
					continue

				try:
					insta_image.instagramify()
				except ValueError as e:
					logger.log.warning("Could not Instagramify file {0} due to {1}".format(f2up,  e))
					continue
				except Exception as e:
					logger.log.warning("Could not Instagramify file {0} due to {1}".format(f2up,  e))
					continue

				#Successfully processed the image for Instagram. Add it to the list
				insta_img_list.append(insta_image)

			#try to identify file based on file extension - VIDEOS
			elif path.splitext(f2up)[1] in configurations.gmail["allowedVideoFormats"]:

				#Instantiate class and load the video in it
				insta_video = InstagramVideo()

				try:
					insta_video.load(VideoFileClip(f2up))
					insta_video.setCaption(new_mail.body)
				except TypeError as e:
					logger.log.warning("Could not load video due to {0}".format(e))
					continue
				except Exception as e:
					logger.log.warning("Could not load video due to {0}".format(e))
					continue

				try:
					insta_video.instagramify()
					#Video may have a new filename. Add to list for later deletion
					if insta_video.video.filename not in at_filelist:
						at_filelist.append(insta_video.video.filename)

				except ValueError as e:
					logger.log.warning("Could not Instagramify file {0} due to {1}".format(f2up,  e))
					continue
				except Exception as e:
					logger.log.warning("Could not Instagramify file {0} due to {1}".format(f2up,  e))
					continue

				#Successfully processed the image for Instagram. Add it to the list
				insta_video_list.append(insta_video)
	#----------------------------------------------------------------------

	#Establish INSTAGRAM connection----------------------------------------
	ia = instagramConnect(configurations) #Instagram

	if not ia:
		logger.log.critical("Failed to logon to Instagram account. Check username/password.".format(e))
		return

	#Loop all the prepared images to upload
	for insta_image in insta_img_list:

		if ia.uploadPhoto(insta_image.image.filename, caption=insta_image.caption):
			logger.log.info("Uploaded photo {0}".format(insta_image.image.filename))
		else:
			logger.log.warning("Failed to upload photo to Instagram account.")

	#Loop all the prepared videos to upload
	for insta_video in insta_video_list:

		if ia.uploadVideo(insta_video.video.filename, insta_video.videoThumb, caption=insta_video.caption):
			logger.log.info("Uploaded video {0}".format(insta_video.video.filename))
		else:
			logger.log.warning("Failed to upload video to Instagram account.")

	logger.log.info("Logging out of Instagram")

	ia.logout()

	#cleanup round
	for f2del in at_filelist:
		try:
			remove(f2del)
			logger.log.info("Deleted file {0}".format(f2del))
		except Exception as e:
			logger.log.warning("Failed to cleanup file {0} due to {1}".format(f2del, e))
	

def test():

	photo_path = '/home/na/gmail2Insta/attachments/'
	pics = ["IMG-20180308-WA0003.jpg", 'logo_bck.png', 'tootall.jpg', 'toconvert.png']
	vids = ["VID-20180315-WA0001.mp4", 'VID-20180318-WA0011.mp4', 'SampleVideo_1280x720_10mb.mp4','SampleVideo_1280x720_2mb.flv']

	#Parsing stage
	try:
		args = arg_parse()
	except Exception as e:
		logger.log.critical("Could not parse arguments due to {0}".format(e))
		return

	#Start by loading the configurations file
	configurations = cfg.Configurations()
	try:
		configurations.load_configurations(args.conf)
	except Exception as e:
		return

	#Loading configurations failed
	if not configurations:
		return

	#Instagram
	try:	
		ia = InstagramAPI(configurations.instagram["username"], configurations.instagram["password"])
	except Exception as e:
		logger.log.critical("Could not initialize instagramAPI due to {0}".format(e))
		return

	try:
		ia.login()
		ia.login()
	except Exception as e:
		logger.log.critical("Could not login to instagram due to {0}".format(e))
		return

	for vid in vids:

		#Instantiate class and load the video in it
		insta_video = InstagramVideo()

		try:
			insta_video.load(VideoFileClip(path.join(photo_path,vid), audio=False))
			insta_video.setCaption("teste")
		except TypeError as e:
			logger.log.warning("Could not load video due to {0}".format(e))
			continue
		except Exception as e:
			logger.log.warning("Could not load video due to {0}".format(e))
			continue

		try:
			insta_video.instagramify()
		except ValueError as e:
			logger.log.warning("Could not Instagramify file {0} due to {1}".format(vid,  e))
			continue
		except Exception as e:
			logger.log.warning("Could not Instagramify file {0} due to {1}".format(vid,  e))
			continue

		print insta_video.video.duration
		print insta_video.video.size


		if ia.isLoggedIn:
			caption = "Sample video"
			ia.uploadVideo(insta_video.video.filename, insta_video.videoThumb, caption=caption)

if __name__ == "__main__":

	#main()
	test()