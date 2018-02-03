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
import os										# used to allow execution of system level commands
import sys
import socket
import requests	
import ConfigParser
from bottle import route, run, template
from pymongo import MongoClient

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# Import my own utilities
sys.path.append(os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),"../"))
# import utilities

# set up logging 
logger = logging.getLogger("BottleLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# load up all the configs
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
# get main DB credentials
db_user = config.get("B3na DB", "user")
db_pass = config.get("B3na DB", "password")

# get our own IP
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("gmail.com",80))
	my_ip = s.getsockname()[0]
	s.close()
	logger.info("Obtained host IP")
except Exception, e:
	log.write(strftime("%H:%M:%S: ")+"Error: Failed to get my IP")
	logger.error("Failed to get host IP")
	logger.error("Traceback "+str(e))

@route('/')
@route('/hello/<name>')
def index(name):
	logger.info("Received request:/hello/"+name)
	return template('<b>Hello {{name}}</b>!', name=name)

run(host=my_ip,port=8080)
