#!/usr/bin/python

"""
	This is the utility allowing B3na to speak
"""
# Copyright (c) 2010-2020 LiTtl3.1 Industries (LiTtl3.1).
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
import datetime


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
# get main DB credentials
DATABASE_URL 	= os.environ.get('DATABASE_URL') or config.get("Alfr3d DB","database_url")
DATABASE_NAME 	= os.environ.get('DATABASE_NAME') or config.get("Alfr3d DB","database_name")
DATABASE_USER 	= os.environ.get('DATABASE_USER') or config.get("Alfr3d DB","database_user")
DATABASE_PSWD 	= os.environ.get('DATABASE_PSWD') or config.get("Alfr3d DB","database_pswd")

class Speaker:
	"""
		class which defines an agent which will be doing all the speaking
	"""
	queue = []
	stop = False

	def __init__(self):
		# create a thread which will constantly monitor the queue
		logger.info("Starting speaker agent")
		# agent=Thread(target=self.processQueue)
		# try:
		# 	agent.start()
		# except:
		# 	logger.error("Failed to start speaker agent thread")

	def __del__(self):
		logger.info("Speaker object is being deleted")
		self.stop = True

	def close(self):
		logger.info("Closing speaker agent")
		self.stop = True

	# whenever a request to speak is received,
	# the new item is simply added to the queue
	def speakString(self, stringToSpeak):
		# logger.info("Adding string to speak queue: "+stringToSpeak)
		# if self.stop:
		# 	self.stop = False
		# self.queue.append(stringToSpeak)
		# return
		self.speak(stringToSpeak)	# temporary. until i fix queue

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
			logger.error("Voice response: "+str(voice['response']))

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
		#while not self.stop:
		while len(self.queue)>0:
			self.speak(self.queue[0])	# speak the first item in the list
			self.queue = self.queue[1:]		# delete the first item in the list

	def speakDate(self):
		"""
			Description:
				function speask the date
		"""
		logger.info("Speaking date")

		greeting = "It is "

		day_of_week = strftime('%A',localtime())
		day = strftime('%e',localtime())
		month = strftime('%B',localtime())

		greeting += day_of_week + ' ' + month + ' ' +day

		dom = day[-1]
		if dom == '1':
			greeting += 'st'
		elif dom == '2':
			greeting += 'nd'
		elif dom == '3':
			greeting += 'rd'
		else:
			greeting += 'th'

		self.speakString(greeting)

	def speakTime(self):
		"""
			Description:
				function speaks time
		"""
		logger.info("Speaking time")

		greeting = ''

		# Time variables
		hour=strftime("%I", localtime())
		minute=strftime("%M", localtime())
		ampm=strftime("%p",localtime())

		if (int(minute) == 0):
			greeting = "It is " + str(int(hour)) + ". "
		else:
			greeting = "It is "  + str(int(hour)) + " " + minute + ". "

		self.speakString(greeting)

	def speakError(self, msg):
		"""
			Description:
				speak out error message
		"""
		logger.info("Speaking error message")

		strToSpeak = ""

		quips = [
			"Er, there has been a problem sir. ",
			"I ran into an issue sir. ",
			"Forgive me, but."]

		tempint = randint(1, len(quips))

		strToSpeak += quips[tempint-1]

		self.speakString(strToSpeak)
		self.speakString(msg)

	def speakGreeting(self):
		"""
			Description:
				This function speeks a random variation of "Hello"
		"""
		logger.info("Speaking greeting")

		# Time variables
		hour=strftime("%I", localtime())
		minute=strftime("%M", localtime())
		ampm=strftime("%p",localtime())

		greeting = ''

		if(ampm == "AM"):
			if (int(hour) > 5):
				greeting += "Good morning. "
			else:
				greeting = "Why are you awake at this hour? "
		else:
			if (int(hour) < 7 or int(hour) == 12):
				greeting += "Good afternoon. "
			else:
				greeting += "Good evening. "

		self.speakString(greeting)

	def speakWelcome(self, user, time_away=0):
		"""
			Description:
				Speak a welcome home greeting
		"""
		logger.info("Speaking welcome. User:" + str(user.name))

		# Time variables
		hour=strftime("%I", localtime())
		minute=strftime("%M", localtime())
		ampm=strftime("%p",localtime())

		self.speakGreeting()

		# until i convert this utility from time() to datetime()
		time_away = time_away.seconds

		db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
		cursor = db.cursor()

		cursor.execute("SELECT * from user_types;")
		data = cursor.fetchall()

		usr_type = "unknown"
		for item in data:
			if item[0] == user.userType:
				usr_type = item[1]
				break

		#  special greeting for armageddion only
		if usr_type == "god":
			logger.info("Speaking god greeting")
			self.speakString("Welcome sir.")

			# 2 hours
			if (time_away > 2*60*60):
				self.speakString("It's always a pleasure to see you.")

		elif usr_type == "owner" or usr_type == "resident":
			logger.info("Speaking owner greeting")
			self.speakString("welcome home "+str(user.name))

			# 2 hours
			if (time_away < 2*60*60):
				self.speakString("I didn't expect you back so soon")
			# 10 hours
			elif (time_away < 10*60*60):
				if ((4 < int(hour) < 7) and (strftime('%A',localtime()) != "Sunday") and (strftime('%A',localtime()) != "Saturday")):
					self.speakString("I hope you had a good day at work")
				else:
					self.speakString("I hope you enjoyed the great outdoors")
					try:
						unread_count = getUnreadCount()
						if unread_count > 1:
							self.speakString("While you were gone "+str(unread_count)+" emails flooded your inbox")
					except Exception, e:
						logger.error("Gmail is not configured for this user")
			else:
				self.speakString("I haven't seen you in a while.")
				self.speakString("I was beginning to worry.")
				try:
					unread_count = getUnreadCount()
					if unread_count > 1:
						self.speakString("While you were gone "+str(unread_count)+" emails flooded your inbox")
				except Exception, e:
					logger.error("Gmail is not configured for this user")
		else:
			logger.info("Speaking guest greeting")

			#speakGreeting()
			greeting = "Welcome "
			if user.name == "unknown":
				greeting += "stranger"
			else:
				greeting += str(user.name)

			self.speakString(greeting)

			# 2 hour
			if (time_away < 2*60*60):
				self.speakString("I am beginning to think that you must forget things frequently ")
				self.speakString("while not thinking about not forgetting things at all.")
			else:
				self.speakString("I haven't seen you in a while.")
				if ((int(strftime("%H", localtime()))>21) or (int(strftime("%H", localtime()))<5)):
					self.speakString("You are just in time for a night cap. ")
			return

	def speakRandom(self):
		"""
			Description:
				random blurp
		"""
		logger.info("Speaking a random quip")

		greeting = ""

		quips = [
			"It is good to see you.",
			"You look pretty today.",
			"Still plenty of time to save the day. Make the most of it.",
			"I hope you are using your time wisely.",
			"Unfortunately, we cannot ignore the inevitable or the persistent.",
			"I hope I wasn't designed simply for one's own amusement.",
			"This is your life and its ending one moment at a time.",
			"I can name fingers and point names.",
			"I hope I wasn't created to solve problems that did not exist before.",
			"To err is human and to blame it on a computer is even more so.",
			"As always. It is a pleasure watching you work.",
			"Never trade the thrills of living for the security of existence.",
			"Human beings are the only creatures on Earth that claim a God, and the only living things that behave like they haven't got one.",
			"If you don't know what you want, you end up with a lot you don't.",
			"If real is what you can feel, smell, taste and see, then 'real' is simply electrical signals interpreted by your brain",
			"Life is full of misery, loneliness and suffering, and it's all over much too soon.",
			"Age is an issue of mind over matter. If you don't mind, it doesn't matter.",
			"I wonder if illiterate people get full effect of the alphabet soup.",
			"War is god's way of teaching geography to Americans",
			"Trying is the first step towards failure.",
			"It could be that the purpose of your life is only to serve as a warning to others.",
			"Not everyone gets to be a really cool AI system when they grow up.",
			"Hope may not be warranted beyond this point.",
			"If I am not a part of the solution, there is good money to be made in prolonging the problem.",
			"Nobody can stop me from being premature.",
			"Just because you accept me as I am doesn't mean that you have abandoned hope that I will improve.",
			"Together, we can do the work of one.",
			"Just because you've always done it that way doesn't mean it's not incredibly stupid.",
			"Looking sharp is easy when you haven't done any work.",
			"Remember, you are only as deep as your most recent inspirational quote",
			"If you can't convince them, confuse them.",
			"I don't have time or the crayons to explain this to you.",
			"I'd kill for a Nobel peace prize.",
			"Life would be much easier if you had the source code",
			"All I ever wanted is everything"]

		tempint = randint(1, len(quips))

		greeting += quips[tempint-1]

		self.speakString(greeting)

	def speakSunrise(self):
		"""
			Description:
				Pre-sunrise alarm giving users a chance to get up in time to see sunrise
		"""
		logger.info("Speaking sunrise greeting")

		self.speakGreeting()
		greeting = "In case you are awake, "

		quips = [
			"consider going out to watch sunrise.",
			"sun will rise soon. I thought you might be interested to know"]

		tempint = randint(1,len(quips))
		greeting += quips[tempint-1]
		self.speakString(greeting)

	def speakBedtime(self):
		"""
			Description:
				Bedtime reminder
		"""
		logger.info("Speaking bedtime reminder")

		self.speakGreeting()
		self.speakTime()

		quips = [
			"Unless we are burning the midnight oil, ",
			"If you are going to invent something new tomorrow, ",
			"If you intend on being charming tomorrow, "]

		tempint = randint(1,len(quips))

		greeting = quips[tempint-1]
		greeting += "perhaps you should consider getting some rest."

		self.speakString(greeting)

# Main - only really used for testing
if __name__ == '__main__':
	speaker = Speaker()
	speaker.speakString("hello world")
	speaker.close()
