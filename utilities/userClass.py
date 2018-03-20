#!/usr/bin/python

"""
	This is a utility for handling the UserClass for Alfr3d:

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
#     and/or distribution of such software/component, that such software/
#     component:
#     a. be disclosed or distributed in source code form;
#     b. be licensed for the purpose of making derivative works; and/or
#     c. can be redistributed only free of enforceable intellectual property
#        rights (e.g. patents); and/or
# (ii) any software/component that contains, is derived in any manner (in whole
#      or in part) from, or statically or dynamically links against any
#      software/component specified under (i).

import os
import logging
import ConfigParser
import socket
import MySQLdb
from datetime import datetime, timedelta

from deviceClass import Device

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("UsersLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/users.log"))
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# load up all the configs
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
# get main DB credentials
DATABASE_URL 	= os.environ.get('DATABASE_URL') or '10.0.0.69'
DATABASE_NAME 	= os.environ.get('DATABASE_NAME') or 'alfr3d'
DATABASE_USER 	= os.environ.get('DATABASE_USER') or 'alfr3d'
DATABASE_PSWD 	= os.environ.get('DATABASE_PSWD') or 'alfr3d'
# DATABASE_URL 	= os.environ.get('DATABASE_URL') or config.get("Alfr3d_DB","database_url")
# DATABASE_NAME 	= os.environ.get('DATABASE_NAME') or config.get("Alfr3d_DB","database_name")
# DATABASE_USER 	= os.environ.get('DATABASE_USER') or config.get("Alfr3d_DB","database_user")
# DATABASE_PSWD 	= os.environ.get('DATABASE_PSWD') or config.get("Alfr3d_DB","database_pswd")

class User:
	"""
		User Class for Alfr3d Users
	"""
	name = 'unknown'
	state = 'offline'
	last_online = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	userType = 'guest'

	def first(self):
		logger.info("Checking for god user")
		self.newUser("armageddion")

	def newUser(self):
		logger.info("Creating a new user")
		db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from user WHERE username = \""+self.name+"\";")
		data = cursor.fetchone()

		try:
			exists = self.getUser(self.name)
		except:
			exists = False
		if exists:
			logger.error("User already exists")
			db.close()
			return False

		logger.info("Creating a new DB entry for user: "+name)
		try:
			cursor.execute("INSERT INTO user(name, state, last_online) \
							VALUES (\""+self.name+"\", \""+self.state+"\", \""+self.last_online+"\" )")
			db.commit()
		except Exception, e:
			logger.error("Failed to update the database")
			logger.error("Traceback: "+str(e))
			db.rollback()
			db.close()
			return False		

		db.close()
		return True

	def getUser(self, name):
		logger.info("Looking for user: " + name)
		db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from user WHERE username = \""+name+"\";")
		data = cursor.fetchone()

		if not data:
			logger.warn("Failed to find user: " +name+ " in the database")
			db.close()
			return False

		print data
		self.name = data[1]
		self.state = data[8]
		self.last_online = data[6]
		self.userType = data[7]

		db.close()
		return True

	def update(self):
		logger.info("Updating user: " + self.name)
		db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from user WHERE username = \""+self.name+"\";")
		data = cursor.fetchone()

		if not data:
			logger.warn("Failed to find a device with MAC: " +self.MAC+ " in the database")
			db.close()
			return False

		logger.info("Device found")
		logger.info(data)

		try:
			cursor.execute("UPDATE user SET username = \" "+self.name+"\" WHERE username = \""+self.name+"\";")
			cursor.execute("UPDATE user SET last_online = \""+datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")+"\" WHERE username = \""+self.name+"\";")
			cursor.execute("SELECT * FROM states;")
			states = cursor.fetchall()
			for state in states:
				if state[1]=='online':
					cursor.execute("UPDATE user SET state_id = "+str(state[0])+" WHERE username = \""+self.name+"\";")
					break
			db.commit()
		except Exception, e:
			logger.error("Failed to update the database")
			logger.error("Traceback: "+str(e))
			db.rollback()
			db.close()
			return False		

		db.close()
		logger.info("Updated user: " + self.name)
		return True

	# refreshes state and last_online for all users
	def refreshAll(self, speaker):		
		logger.info("Refreshing users")
		
		db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from user;")
		data = cursor.fetchall()

		# figure out device types
		dev_types = {}
		cursor.execute("SELECT * FROM device_types;")
		types = cursor.fetchall()
		for type in types:
			dev_types[type[1]]=type[0]

		# figure out states
		stat = {}
		cursor.execute("SELECT * FROM states;")
		states = cursor.fetchall()
		for state in states:
			stat[state[1]]=state[0]			

		# get all devices for that user
		for user in data:
			self.getUser(user[1])
			logger.info("refreshing user "+self.name)			
			last_online=self.last_online

			# get all devices for that user
			try:
				logger.info("Fetching user devices")
				cursor.execute("SELECT * FROM device WHERE user_id = "+str(user[0])+" and device_type_id != "+str(dev_types['HW'])+";")
				devices = cursor.fetchall()
				for device in devices:
					# update last_online time for that user
					if device[4] > user[6]:
						logger.info("Updating user "+self.name)
						print "UPDATE user SET last_online = \""+device[4]+"\" WHERE username = \""+user[1]+"\";"
						cursor.execute("UPDATE user SET last_online = \""+device[4]+"\" WHERE username = \""+user[1]+"\";")
						db.commit()
						last_online = device[4]
			except Exception, e:
				logger.error("Failed to update the database")
				logger.error("Traceback: "+str(e))
				db.rollback()
				continue	

			# this time only needs to account for one cycle of alfr3d's standard loop
			# or a few... in case one of them misses it :) 
			try:
				time_now = datetime.utcnow()
				delta = time_now-last_online
			except Exception, e:
				logger.error("Failed to figure out the timedelta")
				delta = timedelta(minutes=60)

			if delta < timedelta(minutes=30):	# 30 minutes
				if self.state == stat['offline']:
					logger.info(self.name+" just came online")
					# welcome the user
					cursor.execute("UPDATE user SET state_id = "+str(stat['online'])+" WHERE  = username = \""+user[1]+"\";")
					#nighttime_auto()	# turn on the lights
				 	# speak welcome
				 	speaker.speakWelcome(self, time() - float(self.last_online))
			else:
				if self.state == stat["online"]:
					logger.info(self.name+" went offline")
					cursor.execute("UPDATE user SET state_id = "+str(stat['offline'])+" WHERE  = username = \""+user[1]+"\";")
					#nighttime_auto()			# this is only useful when alfr3d is left all alone

			try:
				db.commit()
			except Exception, e:
				logger.error("Failed to update the database")
				logger.error("Traceback: "+str(e))
				db.rollback()
				db.close()
				continue					

		db.close()
		return True