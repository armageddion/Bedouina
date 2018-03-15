#!/usr/bin/python

"""
	This is a utility for handling the Device Class for Alfr3d:
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
import socket
import ConfigParser
import MySQLdb
from datetime import datetime, timedelta

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("DevicesLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/devices.log"))
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

class Device:
	"""
		Device Class for Alfr3d Users' devices
	"""
	name = 'unknown'
	IP = '0.0.0.0'
	MAC = '00:00:00:00:00:00'
	state = 'offline'
	last_online = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	user = 'unknown'
	deviceType = 'guest'

	# mandatory to pass MAC for robustness
	def newDevice(self, mac):
		logger.info("Creating a new device")
		db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from device WHERE MAC = \""+mac+"\";")
		data = cursor.fetchone()

		if data:
			logger.warn("device already exists.... aborting")
			db.close()
			return False

		logger.info("Creating a new DB entry for device with MAC: "+member)
		try:
			cursor.execute("INSERT INTO device(name, IP, MAC, state, last_online, user) \
							VALUES (\""+self.name+"\", \""+self.IP+"\", \""+self.MAC+"\",  \""+self.state+"\",  \""+self.last_online+"\",  \""+self.user+"\")")
			db.commit()
		except Exception, e:
			logger.error("Failed to update the database")
			logger.error("Traceback: "+str(e))
			db.rollback()
			db.close()
			return False			

		db.close()
		return True

	def getDevice(self,mac):
		logger.info("Looking for device with MAC: " + mac)
		db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from device WHERE MAC = \""+mac+"\";")
		data = cursor.fetchone()

		if not data:
			logger.warn("Failed to find a device with MAC: " +mac+ " in the database")
			db.close()
			return False

		logger.info("Device found")
		logger.info(data)

		self.name = data[1]
		self.IP = data[2]
		self.MAC = data[3] 
		self.state = data[7]
		self.last_online = data[4]
		self.user = data[5]
		self.deviceType = data[8]

		db.close()
		return True

	# update entire object in DB with latest values
	def update(self):
		logger.info("Updating device with MAC: " + self.MAC)
		db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from device WHERE MAC = \""+self.MAC+"\";")
		data = cursor.fetchone()

		if not data:
			logger.warn("Failed to find a device with MAC: " +self.MAC+ " in the database")
			db.close()
			return False

		logger.info("Device found")
		logger.info(data)

		try:
			cursor.execute("UPDATE device SET name = \" "+self.name+"\" WHERE MAC = \""+self.MAC+"\";")
			cursor.execute("UPDATE device SET IP = \" "+self.IP+"\" WHERE MAC = \""+self.MAC+"\";")
			cursor.execute("UPDATE device SET last_online = \""+datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")+"\" WHERE MAC = \""+self.MAC+"\";")
			cursor.execute("SELECT * FROM states;")
			states = cursor.fetchall()
			for state in states:
				if state[1]=='online':
					print state[0]
					cursor.execute("UPDATE device SET state_id = "+str(state[0])+" WHERE MAC = \""+self.MAC+"\";")
					break
			db.commit()
		except Exception, e:
			logger.error("Failed to update the database")
			logger.error("Traceback: "+str(e))
			db.rollback()
			db.close()
			return False		

		db.close()
		logger.info("Updated device with MAC: " + self.MAC)
		return True

	def refreshAll(self):
		logger.info("Refreshing device list")
		
		db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from device;")
		data = cursor.fetchall()

		# get all devices for that user
		for device in data:
			logger.info("refreshing device "+device[1])

			# for my devices 5 minute timeout here is more than enough
			# for most devices 15 minutes is fine
			# however, some (brand new) tech is being clever about power saving and if unused will
			# be dormant and, from my observations, only connect once every 20 minutes or so. 
			try:
				last_online = device[4]
				time_now = datetime.utcnow()
				delta = time_now-last_online
			except Exception, e:
				logger.error("Failed to figure out the timedelta")
				delta = timedelta(minutes=60)

			stat = {}
			cursor.execute("SELECT * FROM states;")
			states = cursor.fetchall()
			for state in states:
				stat[state[1]]=state[0]

			try:
				if delta < timedelta(minutes=30):
					cursor.execute("UPDATE device SET state_id = "+str(stat['online'])+" WHERE MAC = \""+device[3]+"\";")
				else:
					cursor.execute("UPDATE device SET state_id = "+str(stat['offline'])+" WHERE MAC = \""+device[3]+"\";")
				db.commit()
			except Exception, e:
				logger.error("Failed to update the database")
				logger.error("Traceback: "+str(e))
				db.rollback()
				db.close()
				return False	

		db.close()
		return True