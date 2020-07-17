#!/usr/bin/python

"""
	This is environment module for Alfr3d
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

import configparser
import os
import re
import sys
import socket
import urllib
import json
import logging
import weatherUtil
import MySQLdb
from time import strftime, localtime

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging
logger = logging.getLogger("EnvironmentLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

config = configparser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
# get main DB credentials
DATABASE_URL 	= os.environ.get('DATABASE_URL') or config.get("Alfr3d DB","database_url")
DATABASE_NAME 	= os.environ.get('DATABASE_NAME') or config.get("Alfr3d DB","database_name")
DATABASE_USER 	= os.environ.get('DATABASE_USER') or config.get("Alfr3d DB","database_user")
DATABASE_PSWD 	= os.environ.get('DATABASE_PSWD') or config.get("Alfr3d DB","database_pswd")

#def checkLocation(method="freegeoip", speaker=None):
def checkLocation(method="freegeoip", speaker=None):
	"""
		Check location based on IP
	"""
	logger.info("Checking environment info")
	# get latest DB environment info
	# Initialize the database
	db = MySQLdb.connect(DATABASE_URL,DATABASE_USER,DATABASE_PSWD,DATABASE_NAME)
	cursor = db.cursor()

	country = 'unknown'
	state = 'unknown'
	city = 'unknown'
	ip = 'unknown'

	try:
		cursor.execute("SELECT * from environment WHERE name = \""+socket.gethostname()+"\";")
		data = cursor.fetchone()

		if data:
			logger.info("Found environment configuration for this host:")
			logger.info("Country: "+str(data[4]))
			logger.info("State: "+str(data[10]))
			logger.info("City: "+str(data[3]))
			logger.info("IP: "+str(data[2]))

			country = data[4]
			state = data[10]
			city = data[3]
			ip = data[2]
		else:
			logger.warning("Failed to find environment configuration for this host")
			logger.info("Creating environment configuration for this host")
			try:
				cursor.execute("INSERT INTO environment (name) \
				VALUES (\""+socket.gethostname()+"\");")
				db.commit()
				logger.info("New environment created")
			except Exception as  e:
				logger.error("Failed to add new environment to DB")
				logger.error("Traceback "+str(e))
				db.rollback()
				db.close()
				return [False, 0, 0]
	except Exception as  e:
		logger.error("Environment check failed")
		logger.error("Traceback "+str(e))

	# placeholders for my ip
	myipv4 = None
	myipv6 = None

	# get my current ip
	logger.info("Getting my IP")
	try:
		myipv4 = urllib.urlopen("http://ipv4bot.whatismyipaddress.com").read()
	except Exception as  e:
		logger.error("Error getting my IPV4")
		myipv4 = None
		logger.error("Traceback "+str(e))
		logger.info("Trying to get our IPV6")
		try:
			myipv6 = urllib.urlopen("http://ipv6bot.whatismyipaddress.com").read()
		except Exception as  e:
			logger.error("Error getting my IPV6")
			logger.error("Traceback "+str(e))
	finally:
		if not myipv6 and not myipv4:
			return [False, 0, 0]

	# get API key for db-ip.com
	apikey = config.get("API KEY", "dbip")

	country_new = country
	state_new = state
	city_new = city
	ip_new = ip
	lat_new = 'n/a'
	long_new = 'n/a'

	if method == 'dbip':
		# get API key for db-ip.com
		apikey = config.get("API KEY", "dbip")
		logger.info("Getting my location - dbip...")

		# get my geo info
		if myipv6:
			url6 = "http://api.db-ip.com/addrinfo?addr="+myipv6+"&api_key="+apikey
		elif myipv4:
			url4 = "http://api.db-ip.com/addrinfo?addr="+myipv4+"&api_key="+apikey

		try:
			# try to get our info based on IPV4
			info4 = json.loads(urllib.urlopen(url4).read().decode('utf-8'))
			print info4 	#DEBUG

			if info4['city']:
				country_new = info4['country']
				state_new = info4['stateprov']
				city_new = info4['city']
				ip_new = info4['address']

			# if that fails, try the IPV6 way
			else:
				info6 = json.loads(urllib.urlopen(url6).read().decode('utf-8'))
				print info6 	#DEBUG

				if info6['country']:
					country_new = info6['country']
					state_new = info6['stateprov']
					city_new = info6['city']
					ip_new = info6['address']

				else:
					raise Exception("Unable to get geo info based on IP")

		except Exception as  e:
				logger.error("Error getting my location:"+e)
				return [False, 0, 0]

	elif method == "freegeoip":
		# get API key for ipstack which was freegeoip.net
		apikey = config.get("API KEY", "ipstack")
		logger.info("Getting my location - freegeoip...")

		if myipv4:
			#url4 = "http://freegeoip.net/json/"+myipv4
			url4 = "http://api.ipstack.com/"+myipv4+"?access_key="+apikey

			try:
				# try to get our info based on IPV4
				info4 = json.loads(urllib.urlopen(url4).read().decode('utf-8'))
				print info4 	#DEBUG
				if info4['city']:
					country_new = info4['country_name']
					#state_new = info4['stateprov_name']
					city_new = info4['city']
					ip_new = info4['ip']
					lat_new = info4['latitude']
					long_new = info4['longitude']

				else:
					raise Exception("Unable to get geo info based on IP")

			except Exception as  e:
				logger.error("Error getting my location:"+str(e))
				return [False, 0, 0]

	else:
		logger.warning("Unable to obtain geo info - invalid method specified")
		return [False, 0, 0]

	# by this point we got our geo info
	# just gotta clean it up because sometimes we get garbage in the city name
	city_new = re.sub('[^A-Za-z]+',"",city_new)
	state_new = state_new.strip()

	logger.info("IP: "+str(ip_new))
	logger.info("City: "+str(city_new))
	logger.info("State/Prov: "+str(state_new))
	logger.info("Country: "+str(country_new))
	logger.info("Longitude: "+str(long_new))
	logger.info("Latitude: "+str(lat_new))

	if city_new == city:
		logger.info("You are still in the same location")
	else:
		logger.info("Oh hello! Welcome to "+city_new)
		if speaker:
			speaker.speakString("Welcome to "+city_new+" sir")
			speaker.speakString("I trust you enjoyed your travels")

		try:
			cursor.execute("UPDATE environment SET country = \""+country_new+"\" WHERE name = \""+socket.gethostname()+"\";")
			cursor.execute("UPDATE environment SET state = \""+state_new+"\" WHERE name = \""+socket.gethostname()+"\";")
			cursor.execute("UPDATE environment SET city = \""+city_new+"\" WHERE name = \""+socket.gethostname()+"\";")
			cursor.execute("UPDATE environment SET IP = \""+ip_new+"\" WHERE name = \""+socket.gethostname()+"\";")
			cursor.execute("UPDATE environment SET latitude = \""+str(lat_new)+"\" WHERE name = \""+socket.gethostname()+"\";")
			cursor.execute("UPDATE environment SET longitude = \""+str(long_new)+"\" WHERE name = \""+socket.gethostname()+"\";")
			db.commit()
			logger.info("Environment updated")
		except Exception as  e:
			logger.error("Failed to update Environment database")
			logger.error("Traceback "+str(e))
			db.rollback()
			db.close()
			return [False, 0, 0]

	db.close()

	# get latest weather info for new location
	try:
		logger.info("Getting latest weather")
		weatherUtil.getWeather(city_new, country_new, speaker)
	except Exception as  e:
		logger.error("Failed to get weather")
		logger.error("Traceback "+str(e))
	return [True, city_new, country_new]

# Main - only really used for testing
if __name__ == '__main__':
	checkLocation()
