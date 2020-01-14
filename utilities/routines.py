#!/usr/bin/python

"""
	This is a utility for Routines for Alfr3d:
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
logger = logging.getLogger("RoutinesLog")
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
DATABASE_URL 	= os.environ.get('DATABASE_URL') or config.get("Alfr3d DB","database_url")
DATABASE_NAME 	= os.environ.get('DATABASE_NAME') or config.get("Alfr3d DB","database_name")
DATABASE_USER 	= os.environ.get('DATABASE_USER') or config.get("Alfr3d DB","database_user")
DATABASE_PSWD 	= os.environ.get('DATABASE_PSWD') or config.get("Alfr3d DB","database_pswd")

# get environment id
db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
cursor = db.cursor()
cursor.execute("SELECT * FROM environment WHERE name = \""+socket.gethostname()+"\";")
env_data = cursor.fetchone()
env_id = env_data[0]
db.close()

routine_list = ["Sunrise","Morning","Sunset","Bedtime"]

def sunriseRoutine(speaker=None):
	"""
		Description:
			sunrise routine - perform this routine 30 minutes before sunrise
			giving the users time to go see sunrise
			### TO DO - figure out scheduling
	"""
	logger.info("Pre-sunrise routine:")

	if speaker == None:
		logger.warning("speaker not supplied")
		return False

	return True

def morningRoutine(speaker=None):
	"""
		Description:
			perform morning routine - ring alarm, speak weather, check email, etc..
	"""
	logger.info("Time for morning routine")

	if speaker == None:
		logger.warning("speaker not supplied")
		return False

	return True

def sunsetRoutine(speaker=None):
	"""
		Description:
			routine to perform at sunset - turn on ambient lights
	"""
	logger.info("Time for sunset routine")

	if speaker == None:
		logger.warning("speaker not supplied")
		return False

	return True

def bedtimeRoutine(speaker=None):
	"""
		Description:
			routine to perform at bedtime - turn on ambient lights
	"""
	logger.info("Bedtime")

	if speaker == None:
		logger.warning("speaker not supplied")
		return False

	return True

def createRoutines():
	"""
		Description:
			check if native routines exist in the DB and create them if
			necessary
	"""
	db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
	cursor = db.cursor()

	for routine in routine_list:
		cursor.execute("SELECT * from routines WHERE name = \""+routine+"\" and environment_id = "+str(env_id)+";")
		data = cursor.fetchone()

		if not data:
			logger.warning("Failed to find routine configuration for "+routine+" routine")
			logger.info("Creating new routine configuration")
			try:
				cursor.execute("INSERT INTO routines (name, environment_id) \
				VALUES (\""+routine+"\","+str(env_id)+");")
				db.commit()
				logger.info("New routine created")
			except Exception, e:
				logger.error("Failed to add new routine to DB")
				logger.error("Traceback "+str(e))
				db.rollback()
				db.close()
				return False

		else:
			logger.info("Routine for "+routine+" already exists..")

	return True

def checkRoutines():
	"""
		Description:
			Check if it is time to execute any routines and take action
			if needed...
	"""
	logger.info("Checking routines")

def resetRoutines():
	"""
		Description:
			reset Triggerd flag for every Enabled routine
	"""
	logger.info("Resetting routine flags")
	db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
	cursor = db.cursor()
	cursor.execute("SELECT * from routines WHERE \
					environment_id = "+str(env_id)+"\
					and enabled = True;")
	routines = cursor.fetchall()

	for routine in routines:
		# set Triggered flag to false
		try:
			logger.info("Resetting 'triggered' flag for "+routine[1]+" routine")
			cursor.execute("UPDATE routines SET triggered = 0 WHERE id = \""+str(routine[0])+"\";")
			db.commit()
		except Exception, e:
			logger.error("Failed to update the database")
			logger.error("Traceback: "+str(e))
			db.rollback()
			db.close()
			return False

	return True

def checkMute():
	"""
		Description:
			checks what time it is and decides if B3na should be quiet
	"""
	logger.info("Checking if B3na should be mute")
	result = False

	db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
	cursor = db.cursor()
	cursor.execute("SELECT * from routines WHERE \
					environment_id = "+str(env_id)+"\
					and name = \"Morning\";")
	morning = cursor.fetchone()
	morning_time = morning[2]

	cursor.execute("SELECT * from routines WHERE \
					environment_id = "+str(env_id)+"\
					and name = \"Bedtime\";")
	bed = cursor.fetchone()
	bed_time = bed[2]

	cur_time = datetime.now()
	mor_time = datetime.now().replace(hour=morning_time.seconds/3600, minute=((morning_time.seconds//60)%60))
	end_time = datetime.now().replace(hour=bed_time.seconds/3600, minute=((bed_time.seconds//60)%60))

	if cur_time > mor_time and cur_time < end_time:
		logger.info("B3na is free to speak during this time of day")
	else:
		logger.info("B3na should be quiet while we're sleeping")
		result = True

	# get state id of status "online"
	cursor.execute("SELECT * from states WHERE state = \"online\";")
	data = cursor.fetchone()
	state = data[0]

	# get all user types which are god or owner type
	cursor.execute("SELECT * from user_types WHERE type = \"owner\" or \
												   type = \"god\";")
	data = cursor.fetchall()
	types = []
	for item in data:
		types.append(item[0])

	# see if any users worth speaking to are online
	cursor.execute("SELECT * from user WHERE state_id = \""+str(state)+"\" and \
											 user_type_id = \""+str(types[0])+"\" or \
										 	 user_type_id = \""+str(types[1])+"\";")
	data = cursor.fetchall()

	if not data:
		logger.info("B3na should be quiet when no worthy ears are around")
		result = True
	else:
		logger.info("B3na has worthy listeners")

	if result:
		logger.info("B3na is to be quiet")
	else:
		logger.info("B3na is free to speak")

	return result
