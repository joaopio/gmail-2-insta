#!/usr/bin/env python

__doc__ = \
'''
'''

__version__ = '0.1'

__authors__ = [
				"Version 0.1: Joao Pio <pio.joao@gmail.com>"
			]

#Standard packages
from os import path, remove

#Third party APIs
from PIL import Image
#required to circumvent InstagramAPI video upload bug. Only downloads the first time this script is executed
try:
	from moviepy.editor import VideoFileClip
except ImportError:
	import imageio
	imageio.plugins.ffmpeg.download()
	from moviepy.editor import VideoFileClip

#Local packages
from tools.g2ilog import logger

class InstagramImage():
	
	#Class Constructor
	def __init__(self):

		#The image object itself
		self.image = None

		#The image caption
		self.caption = None

		#allowed aspect ratios interval
		self.allowedAspectInterval = [0.8, 1.91]

		#aspect ratios interval of photos that can be resized without too much distortion
		self.resizableAspectInterval = [0.5, 2.1]

		#Maximum allowed width for an image in instagram
		self.maxWidth = 1080

		#Maximum allowed number of characters for an Instagram caption
		self.maxCaptionChars = 2200

		#Allowed instagram maximum image dimensions in pixels as of January 2018
		self.allowedMaxDims = {"square": (1080, 1080), "portrait": (1080, 1350), "landscape": (1080, 566)}

	#Loads a PIL.Image.Image object
	def load(self, image):
		if isinstance(image, Image.Image):
			self.image = image
		else:
			raise TypeError("Image must be an instance of PIL.Image.Image")

	def setCaption(self, caption):

		if isinstance(caption, str):
			if len(caption) > 2200:
				self.caption = caption[2199]
			else:
				self.caption = caption
		else:
			raise TypeError("Caption must be an instance of String")
		

	#Method to calculate the best size for this image
	def calculateBestSize(self):

		if self.image == None:
			logger.log.error("No image loaded yet")
			return None

		#calculate the current aspect ratio
		try:
			aspect_ratio = float(self.image.size[0])/float(self.image.size[1])
		except ZeroDivisionError as e:
			logger.log.warning("Height of image is zero. Ignoring image.")
			return None

		#First check if aspect ratio is workable
		if self.resizableAspectInterval[0] <= aspect_ratio <= self.resizableAspectInterval[1]:
			pass
		#Does not allow for a resizable picture without too much distortion. Consider cropping.
		else:
			return None

		#Second check if image is within the allowed aspect ratios
		if self.allowedAspectInterval[0] <= aspect_ratio <= self.allowedAspectInterval[1]:
			#Image is within range, so let's check the maximum width 1080
			if self.image.size[0] <= self.maxWidth:
				#No changes needed
				return self.image.size
			#Width is above maximum. Reduce it to the max and recalculate Height
			else:
				height = int(self.maxWidth / aspect_ratio)

				#1080xheight
				return (self.maxWidth, height)
		#Aspect ratio is off. Correct it.
		else:
			#check if max width is exceeded
			if self.image.size[0] > self.maxWidth:
				#Width should be reduced to maxWidth
				width = self.maxWidth
			else:
				#Keep the current width
				width = self.image.size[0]

			#Handle the height now
			#It's portrait
			if aspect_ratio < self.allowedAspectInterval[0]:
				#Just multiply the width for the minimum allowed aspect ratio and get the height
				height = int(width / self.allowedAspectInterval[0])

				return (width, height)

			#It's landscape
			elif aspect_ratio > self.allowedAspectInterval[1]:
				#Just multiply the width for the minimum allowed aspect ratio and get the height
				height = int(width / self.allowedAspectInterval[1])

				return (width, height)
			
			else:
				return None

	#Converts and resizes images to accomodate Instagram's policies
	def instagramify(self):

		#save file and filepath due to loss of image.filename on resize
		filename = path.basename(self.image.filename)
		filepath = path.dirname(self.image.filename)

		#Resize the image to conform to Instagram requirements
		new_size = self.calculateBestSize()

		if new_size is not None:
			self.image = self.image.resize(new_size)
			logger.log.info("Resized {0} to {1} pixels".format(path.join(filepath, filename), self.image.size))
			self.image.filename = path.join(filepath, filename)
		else:
			raise ValueError("Image {0} had an abnormal set of dimensions.".format(path.join(filepath, filename)))		

		#verify if format is jpeg and convert accordingly
		if self.image.format != "JPEG":
			#convert image to jpg
			self.image.save(path.join(filepath, filename), "JPEG")


class InstagramVideo(VideoFileClip):
	
	#Class Constructor
	def __init__(self):

		#The video object itself
		self.video = None

		#The video thumbnail
		self.videoThumb = None

		#allowed aspect ratios interval
		self.allowedAspectInterval = [0.8, 1.91]

		#aspect ratios interval of videos that can be resized without too much distortion
		self.resizableAspectInterval = [0.5, 2.1]

		#Maximum allowed width for an video in instagram
		self.maxWidth = 1080

		#Allowed instagram maximum video dimensions in pixels as of January 2018
		self.allowedMaxDims = {"square": (1080, 1080), "portrait": (1080, 1350), "landscape": (1080, 566)}

		#Allowed instagram video length in seconds (min, max)
		self.allowedLength = (3,60)

		#Allowed instagram video frame rate
		self.allowedFrameRate = 29.96

		#Allowed instagram video kbps
		self.allowedKbps = 5.500

	#Loads a movie.VideoFileClip object
	def load(self, video):
		if isinstance(video, VideoFileClip):
			self.video = video
		else:
			raise TypeError("Video must be an instance of moviepy.editor.VideoFileClip")

	def setCaption(self, caption):

		if isinstance(caption, str):
			if len(caption) > 2200:
				self.caption = caption[2199]
			else:
				self.caption = caption
		else:
			raise TypeError("Caption must be an instance of String")

	#Method to calculate the best size for this video
	def calculateBestSize(self):

		if self.video == None:
			logger.log.error("No video loaded yet")
			return None

		#First check if aspect ratio is workable
		if self.resizableAspectInterval[0] <= self.video.aspect_ratio <= self.resizableAspectInterval[1]:
			pass
		#Does not allow for a resizable picture without too much distortion. Consider cropping.
		else:
			return None

		#Second check if image is within the allowed aspect ratios
		if self.allowedAspectInterval[0] <= self.video.aspect_ratio <= self.allowedAspectInterval[1]:
			#Image is within range, so let's check the maximum width 1080
			if self.video.size[0] <= self.maxWidth:
				#No changes needed
				return self.video.size
			#Width is above maximum. Reduce it to the max and recalculate Height
			else:
				height = int(self.maxWidth / self.video.aspect_ratio)

				#1080xheight
				return (self.maxWidth, height)
		#Aspect ratio is off. Correct it.
		else:
			#check if max width is exceeded
			if self.video.size[0] > self.maxWidth:
				#Width should be reduced to maxWidth
				width = self.maxWidth
			else:
				#Keep the current width
				width = self.video.size[0]

			#Handle the height now
			#It's portrait
			if self.video.aspect_ratio < self.allowedAspectInterval[0]:
				#Just multiply the width for the minimum allowed aspect ratio and get the height
				height = int(width / self.allowedAspectInterval[0])

				return (width, height)

			#It's landscape
			elif self.video.aspect_ratio > self.allowedAspectInterval[1]:
				#Just multiply the width for the minimum allowed aspect ratio and get the height
				height = int(width / self.allowedAspectInterval[1])

				return (width, height)
			
			else:
				return None

	#Converts and resizes images to accomodate Instagram's policies
	def instagramify(self):

		#save file and filepath due to loss of video.filename on resize
		filename = path.basename(self.video.filename)
		filepath = path.dirname(self.video.filename)
		filext = path.splitext(self.video.filename)[1]

		#Build target filename
		if filext != "mp4":
			target_filename = "{0}.mp4".format(path.splitext(self.video.filename)[0])
		else:
			target_filename = filename

		#Resize the image to conform to Instagram requirements
		new_size = self.calculateBestSize()

		if new_size is None:
			raise ValueError("Video {0} had an abnormal set of dimensions.".format(path.join(filepath, filename)))		
		elif new_size != self.video.size:
			self.video = self.video.resize(new_size)
			logger.log.info("Resized {0} to {1} pixels".format(path.join(filepath, filename), self.video.size))

		#Create the thumbnail for the video
		thumb = "{0}.jpg".format(path.splitext(filename)[0])
		self.videoThumb = path.join(filepath,thumb)
		self.video.save_frame(self.videoThumb, t=4.00)
		
		#Rename the file and save it to the disk
		self.video.filename = path.join(filepath, target_filename)
		self.video.write_videofile(filename=self.video.filename, audio=False, codec="libx264")
			

		