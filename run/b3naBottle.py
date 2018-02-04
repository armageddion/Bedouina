#!/usr/bin/python

"""
	This is the main B3na restful API interfact
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
import json
import ConfigParser
import bottle
from bottle import route, run, template, request
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
db_user = config.get("Alfr3d DB", "user")
db_pass = config.get("Alfr3d DB", "password")

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

class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors

app = bottle.app()

@route('/')
@route('/hello/<name>')
def index(name):
	logger.info("Received request:/hello/"+name)
	return template('<b>Hello {{name}}</b>!', name=name)

@app.route('/whosthere', method=['OPTIONS','GET'])
def whosthere():
	logger.info("Received a 'whosthere' requet")

	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']
	usersCollection = db['users']

	count = 0
	users = []

	# cycle through all users
	#for user in usersCollection.find():
	for user in usersCollection.find({"$and":[
											{"state":'online'},
											{"location.name":socket.gethostname()}
										]}):
			count +=1
			users.append(user['name'])

	result = {}
	result['location'] = socket.gethostname()
	if count > 0:
		result['users']=[]
		for i in range(len(users)):
			result['users'].append(users[i])
	else:
		result['users']=0

	return json.dumps(result)

@route('/make_coffee')
def make_coffee():
	# IFTTT https://maker.ifttt.com/use/cKPaEEmi5bh7AY_H16g3Ff
	# https://maker.ifttt.com/trigger/make_coffee/with/key/cKPaEEmi5bh7AY_H16g3Ff

	logger.info("Received a request to make coffee")

	result = {}

	secret = config.get("API KEY", "ifttt_hook")

	coffe_request = requests.post("https://maker.ifttt.com/trigger/make_coffee/with/key/"+str(secret))
	if coffe_request.status_code == 200:
		logger.info("coffee is being made")		
		result['status']="OK"
	else:
		logger.error("something went wrong... cannot make coffee")
		result['status']="ERROR"
		result['error code']=str(coffe_request.status_code)

	return json.dumps(result)

# http://b3na.littl31.com:8080/water_flowers
# http://b3na.littl31.com:8080/water_flowers?timeout=200
@route('/water_flowers')
def water_flowers():
	logger.info("Received request to water the flowers")
	secret = config.get("API KEY", "ifttt_hook")

	timeout = 30

	try: 
		timeout=int(request.query.timeout)
	except:
		logger.warn("Timeout not provided")

	result = {}

	flower_on_request = requests.post("https://maker.ifttt.com/trigger/water_flowers/with/key/"+str(secret))
	if flower_on_request.status_code == 200:
		logger.info("Successfully turned on the irrigation system")
		result['status pump on']="OK"

		time.sleep(timeout)
		
		flower_off_request = requests.post("https://maker.ifttt.com/trigger/water_flowers_end/with/key/"+str(secret))
		if flower_off_request.status_code == 200:
			logger.info("Successfully turned off the irrigation system")
			result['status pump off']="OK"
		else:
			logger.error("Something went wrong. unable to turn off the irrigation system")
			result['status pump off']="OK"
			result['comment']="something went wrong... no bueno"
	else:
		logger.error("Something went wrong. unable to turn off the irrigation system")
		result['status']="ERROR"
		result['error code']=str(coffe_request.status_code)		

	return json.dumps(result)

# http://b3na.littl31.com:8080/lights?all=on
@route('/lights')
def lights():
	logger.info("Received request to command the lights: "+str(request.query_string))

	result = {}

	if len(request.query)==0:
		result['status']="ERROR"
		result['details']="you didn't provide any args... "
	else:
		if request.query.all == "on":
			logger.info("Processing command")
			utilities.lightingOn()				# TODO: need to return a value for proper processing
			result['status']="OK"
			result['details']='processing request to turn the lights off'
		elif request.query.all == "off":
			logger.info("Processing command")
			utilities.lightingOff()				# TODO: need to return a value for proper processing
			result['status']="OK"
			result['details']='processing request to turn the lights on'
		else:
			logger.warn("Received request to command the lights: "+str(request.query_string))
			logger.warn("But I dont know how to process it yet")
			result['status']="ERROR"
			result['details']='i dont know how to process that request yet'

	return json.dumps(result)

app.install(EnableCors)	
app.run(host=my_ip,port=8080)
