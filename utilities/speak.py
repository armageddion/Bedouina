#!/usr/bin/python

"""
	This is the utility allowing B3na to speak
"""
# Copyright (c) 2010-2018 LiTtl3.1 Industries (LiTtl3.1).
# All rights reserved.
# This source code and any compilation or derivative thereof is the
# proprietary information of LiTtl3.1 Industries and is
# confidential in nature.
# Use of this source code is subject to the terms of the applicable
# LiTtl3.1 Industries license agreement.
#
# Under no circumstances is this component (or portion thereof) to be in any
# way affected or brought under the terms of any Open Source License without
# the prior express written permission of LiTtl3.1 Industries.
#
# For the purpose of this clause, the term Open Source Software/Component
# includes:
#
# (i) any software/component that requires as a condition of use, modification
#	 and/or distribution of such software/component, that such software/
#	 component:
#	 a. be disclosed or distributed in source code form;
#	 b. be licensed for the purpose of making derivative works; and/or
#	 c. can be redistributed only free of enforceable intellectual property
#		rights (e.g. patents); and/or
# (ii) any software/component that contains, is derived in any manner (in whole
#	  or in part) from, or statically or dynamically links against any
#	  software/component specified under (i).
#

import ConfigParser
import os
import sys
import logging
import socket									# needed to get hostname
from random import randint						# used for random number generator
from threading import Thread
from time import strftime, localtime, time, sleep
from gmail import getUnreadCount

# import my own utilities
sys.path.append(os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),"../"))
import third_party

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("SpeakLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/speak.log"))
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# get API key for db-ip.com
config = ConfigParser.RawConfigParser()
config.read(os.path.join(CURRENT_PATH,'../conf/apikeys.conf'))
apikey = config.get("API KEY", "voicerss")

class Speaker:
	"""
		class which defines an agent which will be doing all the speaking
	"""
	queue = []
	stop = False

	def __init__(self):
		# create a thread which will constantly monitor the queue
		logger.info("starting speaker agent on another thread")
		agent=Thread(target=self.processQueue)
		try:
			agent.start()
		except:
			logger.error("Failed to start speaker agent thread")

	def close(self):
		logger.info("Closing speaker agent")
		self.stop = True

	# whenever a request to speak is received,
	# the new item is simply added to the queue
	def speakString(self, stringToSpeak):
		logger.info("Adding string to speak queue: "+stringToSpeak)
		self.queue.append(stringToSpeak)

	# speaking happens heare
	def speak(self,string):
		"""
			Description:
				This function convertrs a given <string> into mp3 using voicerss
				and then plays it back
		"""
		logger.info("Speaking "+str(string))

		try:
			voice = third_party.speech({
				'key': apikey,
				'hl': 'en-gb',
				'src': string,
				'r': '0',
				'c': 'mp3',
				'f': '44khz_16bit_stereo',
				'ssml': 'false',
				'b64': 'false'
			})
		except Exception, e:
			logger.error("Failed to get TTS sound file")
			logger.error("Traceback: "+str(e))

		try:
			outfile = open(os.path.join(CURRENT_PATH,'../tmp/audio.mp3'),"w")
			outfile.write(voice['response'])
			outfile.close()
		except Exception, e:
			logger.error("Failed to write sound file to temporary directory")
			logger.error("Traceback: "+str(e))

		try:			
			os.system('mplayer -really-quiet -noconsolecontrols '+os.path.join(CURRENT_PATH,'../tmp/audio.mp3')) 	# old alfr3d on RPI2
		except Exception, e:
			logger.error("Failed to play the sound file using mplayer")
			logger.error("Traceback: "+str(e))
			logger.info("Trying another one")
			try:
				os.system('omxplayer -o local '+os.path.join(CURRENT_PATH,'../tmp/audio.mp3'))			# RPI3
			except Exception, e:
				logger.error("Failed to play the sound file using omxplayer")
				logger.error("Traceback: "+str(e))
				logger.info("Trying another one")	

	def processQueue(self):
		while True:
			if self.stop:
				return
			while len(self.queue)>0:
				self.speak(self.queue[0])	# speak the first item in the list
				self.queue = self.queue[1:]		# delete the first item in the list


# Main - only really used for testing
if __name__ == '__main__':
	speaker = Spekaer()
	speaker.speakString("hello world")
	speaker.close()