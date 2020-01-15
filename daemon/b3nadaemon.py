 #!/usr/bin/python

"""
	This is the main B3na daemon running most standard services
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

# Imports
import logging
import time
import os						# used to allow execution of system level commands
import sys
import schedule					# 3rd party lib used for alarm clock managment.
import datetime
import ConfigParser				# used to parse alfr3ddaemon.conf
from threading import Thread
from daemon import Daemon
from random import randint		# used for random number generator

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# import my own utilities
sys.path.append(os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),"../"))
import utilities
# import reporting

masterSpeaker = utilities.Speaker()

# set up daemon things
os.system('sudo mkdir -p /var/run/b3nadaemon')
#os.system('sudo chown alfr3d:alfr3d /var/run/alfr3ddaemon')

# load up all the configs
config = ConfigParser.RawConfigParser()
config.read(os.path.join(CURRENT_PATH,'../conf/apikeys.conf'))
# get main DB credentials
DATABASE_URL 	= os.environ.get('DATABASE_URL') or config.get("Alfr3d DB","database_url")
DATABASE_NAME 	= os.environ.get('DATABASE_NAME') or config.get("Alfr3d DB","database_name")
DATABASE_USER 	= os.environ.get('DATABASE_USER') or config.get("Alfr3d DB","database_user")
DATABASE_PSWD 	= os.environ.get('DATABASE_PSWD') or config.get("Alfr3d DB","database_pswd")

# gmail unread count
UNREAD_COUNT = 0
UNREAD_COUNT_NEW = 0

# time of sunset/sunrise - defaults
# SUNSET_TIME = datetime.datetime.now().replace(hour=19, minute=0)
# SUNRISE_TIME = datetime.datetime.now().replace(hour=6, minute=30)
# BED_TIME = datetime.datetime.now().replace(hour=23, minute=00)

# various counters to be used for pacing spreadout functions
QUIP_START_TIME = time.time()
QUIP_WAIT_TIME = randint(5,10)

# set up logging
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)


class MyDaemon(Daemon):
	def run(self):
		while True:
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				Logging Examples:
				logger.debug("Debug message")
				logger.info("Info message")
				logger.warn("Warning message")
				logger.error("Error message")
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

			# OK Take a break
			time.sleep(10)

			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				Check online members
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
			try:
				logger.info("Scanning network")
				utilities.checkLANMembers(masterSpeaker)
			except Exception, e:
				logger.error("Failed to complete network scan")
				masterSpeaker.speakError("I failed to complete the network scan")
				logger.error("Traceback: "+str(e))

			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				Things to do only during waking hours and only when
				god or owner is in tha house
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
			mute = utilities.checkMute()
			if not mute:
				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
					Things to do only during waking hours and only when
					god is in tha house
				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				try:
					logger.info("Is it time for a smartass quip?")
					self.beSmart()
				except Exception, e:
					logger.error("Failed to complete the quip block")
					masterSpeaker.speakError("I failed in being a smart arse")
					logger.error("Traceback: "+str(e))

				# check emails
				try:
					logger.info("Checking Gmail")
					self.checkGmail()
				except Exception, e:
					logger.error("Failed to check Gmail")
					masterSpeaker.speakError("I have been unable to check your mail")
					logger.error("Traceback: "+str(e))

	def checkGmail(self):
		"""
			Description:
				Checks the unread count in gMail
		"""
		logger.info("Checking email")
		global UNREAD_COUNT
		global UNREAD_COUNT_NEW

		UNREAD_COUNT_NEW = utilities.getUnreadCount()

		if (UNREAD_COUNT < UNREAD_COUNT_NEW):
			logger.info("A new email has arrived...")

			logger.info("Speaking email notification")
			email_quips = [
				"Yet another email",
				"Pardon the interruption sir. Another email has arrived for you to ignore."]

			tempint = randint(1,len(email_quips))
			masterSpeaker.speakString(email_quips[tempint-1])

		if (UNREAD_COUNT_NEW != 0):
			logger.info("Unread count: "+str(UNREAD_COUNT_NEW))

	def beSmart(self):
		"""
			Description:
				speak a quip
		"""
		global QUIP_START_TIME
		global QUIP_WAIT_TIME

		if time.time() - QUIP_START_TIME > QUIP_WAIT_TIME*60:
			logger.info("It is time to be a smartass")

			masterSpeaker.speakRandom()

			QUIP_START_TIME = time.time()
			QUIP_WAIT_TIME = randint(10,50)
			print "Time until next quip: ", QUIP_WAIT_TIME 	#DEBUG

			logger.info("QUIP_START_TIME and QUIP_WAIT_TIME have been reset")
			logger.info("Next quip will be shouted in "+str(QUIP_WAIT_TIME)+" minutes.")

	def playTune(self):
		"""
			Description:
				pick a random song from current weather category and play it
		"""
		logger.info("playing a tune")

	def nightlight(self):
		"""
			Description:
				is anyone at home?
				is it after dark?
				turn the lights on or off as needed.
		"""
		logger.info("nightlight auto-check")

def sunriseRoutine():
	"""
		Description:
			sunset routine - perform this routine 30 minutes before sunrise
			giving the users time to go see sunrise
			### TO DO - figure out scheduling
	"""
	logger.info("Pre-sunrise routine")

def morningRoutine():
	"""
		Description:
			perform morning routine - ring alarm, speak weather, check email, etc..
	"""
	logger.info("Time for morning routine")

def sunsetRoutine():
	"""
		Description:
			routine to perform at sunset - turn on ambient lights
	"""
	logger.info("Time for sunset routine")

def bedtimeRoutine():
	"""
		Description:
			routine to perform at bedtime - turn on ambient lights
	"""
	logger.info("Bedtime")

def resetRoutines():
	"""
		Description:
			refresh some things at midnight
	"""
	utilities.resetRoutines()


def init_daemon():
	"""
		Description:
			initialize alfr3d services
	"""
	logger.info("Initializing systems check")
	initSpeaker = utilities.Speaker()
	initSpeaker.speakString("Initializing systems check")

	# check and create god user if it doesn't exist
	user = utilities.User()
	user.first()

	faults = 0

	# initial geo check
	try:
		initSpeaker.speakString("Running geo scan")
		logger.info("Running a geoscan")
		ret = utilities.checkLocation("freegeoip", speaker=initSpeaker)
		if not ret[0]:
			raise Exception("Geo scan failed")
		initSpeaker.speakString("Geo scan complete")
	except Exception, e:
		initSpeaker.speakString("Failed to complete geo scan")
		logger.error("Failed to complete geoscan scan")
		logger.error("Traceback: "+str(e))
		faults+=1

	# set up some routine schedules
	try:
		initSpeaker.speakString("Setting up scheduled routines")
		logger.info("Setting up scheduled routines")
		utilities.createRoutines()
		resetRoutines()

		# "8.30" in the following function is just a placeholder
		# until i deploy a more configurable alarm clock
		schedule.every().day.at("00:05").do(resetRoutines)
		#schedule.every().day.at(str(bed_time.hour)+":"+str(bed_time.minute)).do(bedtimeRoutine)
	except Exception, e:
		initSpeaker.speakString("Failed to set schedules")
		logger.error("Failed to set schedules")
		logger.error("Traceback: "+str(e))
		faults+=1												# bump up fault counter

	initSpeaker.speakString("Systems check complete")
	if faults != 0:
		initSpeaker.speakString("Some faults were detected but system started successfully")
		initSpeaker.speakString("Total number of faults is "+str(faults))
	else:
		initSpeaker.speakString("All systems are up and operational")

	initSpeaker.close()
	return

if __name__ == "__main__":
	#daemon = MyDaemon('/var/run/b3nadaemon/b3nadaemon.pid',stderr='/dev/null')
	daemon = MyDaemon('/var/run/b3nadaemon/b3nadaemon.pid',stderr='/dev/stderr')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			logger.info("B3na Daemon initializing")
			faults = init_daemon()
			logger.info("B3na Daemon starting...")
			daemon.start()
		elif 'stop' == sys.argv[1]:
			logger.info("B3na Daemon stopping...")
			daemon.stop()
			sys.exit(1)
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
