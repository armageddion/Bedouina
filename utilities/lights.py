#!/usr/bin/python

"""
	This file is used for all weather related functions.
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
#

import json											# used to handle jsons returned from www
import urllib										# used to make calls to www
import os											# used to allow execution of system level commands
import logging										# needed for useful logs
import socket
import ConfigParser
import MySQLdb
from datetime import datetime
from time import gmtime, strftime, localtime		# needed to obtain time

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging
logger = logging.getLogger("LightsLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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

def lightingOn(lights="all"):
	logger.info("turning the lights "+lights+ "on")

	# find all lights in the database
	db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
	cursor = db.cursor()
	# find id for lights
	cursor.execute("SELECT * FROM device_types WHERE type = 'HW_lights';")
	dev_type = cursor.fetchone()[0]
	# find id for environment
	cursor.execute("SELECT * FROM environment WHERE name = \""+socket.gethostname()+"\";")
	env_id = cursor.fetchone()[0]

	if lights == "all":
		# find all lights in our environment
		cursor.execute("SELECT * FROM device WHERE device_type_id = "+str(dev_type)+" AND environment_id = "+str(env_id)+";")
		devices = cursor.fetchall()
		for device in devices:
			print "switching device"+ device[0] + "on"
			#TODO
	else:
		print "SELECT * FROM device WHERE device_type_id = "+str(dev_type)+" AND environment_id = "+str(env_id)+" AND name = "+lights+";" # DEBUG
		cursor.execute("SELECT * FROM device WHERE device_type_id = "+str(dev_type)+" AND environment_id = "+str(env_id)+" AND name = "+lights+";")
		device = cursor.fetchone()
		print "switching device"+ device[0] + "on"
		#TODO

	return True

def lightingOff(lights="all"):
	logger.info("turning the lights "+lights+ "off")

	# find all lights in the database
	db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
	cursor = db.cursor()
	# find id for lights
	cursor.execute("SELECT * FROM device_types WHERE device_type == 'HW_lights';")
	dev_type = cursor.fetchone()[0]
	# find id for environment
	cursor.execute("SELECT * FROM environment WHERE name = \""+socket.gethostname()+"\";")
	env_id = cursor.fetchone()[0]

	if lights == "all":
		# find all lights in our environment
		cursor.execute("SELECT * FROM device WHERE device_type_id = "+str(dev_type)+" AND environment_id = "+str(env_id)+";")
		devices = cursor.fetchall()
		for device in devices:
			print "switching device"+ device[0] + "off"
			#TODO
	else:
		cursor.execute("SELECT * FROM device WHERE device_type_id = "+str(dev_type)+" AND environment_id = "+str(env_id)+" AND name = "+lights+";")
		device = cursor.fetchone()
		print "switching device"+ device[0] + "off"
		#TODO

	return True

# purely for testing purposes
if __name__ == "__main__":
	print "testing the lights"
