#!/usr/bin/python

"""
	This is Spotify utility for B3na. Original was written by Jimbob 
	as a shell script.
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

import os
import sys
import json
import base64
import logging
import urllib
import urllib2
import requests
import spotipy
import spotipy.util as sp_util
import ConfigParser

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging
logger = logging.getLogger("SpotifyLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/users.log"))
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# load up all the configs
configfile = os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf')
config = ConfigParser.RawConfigParser()
config.read(configfile)

#=====================================
# Account Config Stuff
#=====================================
CLIENT_ID = os.environ.get("SPOTIFY_CLID") or config.get("Spotify","id")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLSEC") or config.get("Spotify","secret")
USERNAME = os.environ.get("SPOTIFY_USERNAME") or config.get("Spotify","username")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT") or config.get("Spotify","redirect_uri")
ACCESS_TOKEN = os.environ.get("SPOTIFY_ACCESS_TOKEN") or config.get("Spotify","access_token")
REFRESH_TOKEN = os.environ.get("SPOTIFY_REFRESH_TOKEN") or config.get("Spotify","refresh_token")
SCOPE='user-library-read streaming user-read-playback-state user-modify-playback-state'
KEY = str(CLIENT_ID)+":"+str(CLIENT_SECRET)
KEY64 = base64.b64encode(KEY.encode())

#====================================
# Device Config Stuff
#==================================
PLAYLIST_ID="4tWK1DAExQ5jqfIjXEMcTS"  # Party Music
PLAYLIST_POSITION="2"
TRACK_START_TIME_MS="80000"

#================================
# Input Params
#===============================
PARTY_STATUS="$1"	# argument 1
ROOM="$2"			# argument 2

#=============================
# Other Config
#=============================
PARTY_START_TRIGGER="on"
PARTY_STOP_TRIGGER="off"

"""
TODO:
 - logging
 - proper caching of access creds
"""
def init_spotify():
	logger.info("Running Spotify init")

	os.environ["SPOTIPY_CLIENT_ID"] = CLIENT_ID
	os.environ["SPOTIPY_CLIENT_SECRET"] = CLIENT_SECRET
	os.environ["SPOTIPY_REDIRECT_URI"] = REDIRECT_URI

	#======================================
	# Step 0: Authorize app
	#======================================
	# TODO: this is tricky because it caches the token in random location... 
	# gotta find a workaround.
	token = sp_util.prompt_for_user_token(username=USERNAME, scope=SCOPE)

	logger.info("Spotify init done")
	return token
		

def main():
	print 'main'

	try:
		refresh_token()
	except Exception as  e:
		logger.error("Failed to refresh Spotify token")
		logger.error("Traceback: "+str(e))
		return		

	try:
		device = find_device()
	except Exception as  e:
		logger.error("Failed to find Alfr3d device")
		logger.error("Traceback: "+str(e))
		return				

	try:
		b3na_play(device=device)
	except Exception as  e:
		logger.error("Failed to start Spotify playback on device")
		logger.error("Traceback: "+str(e))
		return		

	print 'end main'


#======================================
# Step 1: Request New Access Token
#======================================
def refresh_token():
	logger.info("Requesting Spotify token refresh")

	url = 'https://accounts.spotify.com/api/token'
	values = {'grant_type' : 'refresh_token',
	          'refresh_token' : REFRESH_TOKEN }
	headers = { "Authorization" : "Basic "+str(KEY64) }

	data = urllib.urlencode(values)
	data = data.encode('ascii')
	req = urllib2.Request(url, data, headers)

	try:
		response = urllib2.urlopen(req)
		the_page = response.read()	
		ret_data = json.loads(the_page)
		# print ret_data		# DEBUG
		# print ("new access_token", ret_data['access_token'])		# DEBUG
		logger.info("Got new Spotify access token")

		global ACCESS_TOKEN
		ACCESS_TOKEN = ret_data['access_token']

	except Exception as  e:
		logger.error("ERROR getting access token. Giving up")
		logger.error("Traceback: "+str(e))
		return

	try:
		logger.info("Updating conf files with new token")
		cfgfile = open(configfile,'w')
		config.set('Spotify','access_token',ret_data['access_token'])
		config.write(cfgfile)
	except Exception as  e:
		logger.error("ERROR updating conf files")
		logger.error("Traceback: "+str(e))
		return

#======================================
# Step 2: Get list of devices
#======================================	
def find_device():
	logger.info("Requesting a list of Spotify playable devices")

	url = 'https://api.spotify.com/v1/me/player/devices'
	headers = { "Authorization" : "Bearer "+ACCESS_TOKEN }

	req = urllib2.Request(url, headers=headers)
	response = urllib2.urlopen(req)
	the_page = response.read()	
	ret_data = json.loads(the_page)

	device = None
	for dev in ret_data['devices']:
		print dev['name']				# DEBUG
		#if dev['name'] == "B3na":
		if dev['name'] == "Shogun": 	# DEBUG
			device = dev
			break

	if not device:
		logger.error("B3na Spotify device not found")
		return
	else:
		logger.info("B3na Spotify device found")
		print device

	return device

#======================================
# Step 3: Play on B3na
#======================================	
def b3na_play(device):
	logger.info("Loading Spotify onto B3na device: "+str(device['id']))

	url = 'https://api.spotify.com/v1/me/player'
	values = {'device_ids' : [device['id']]}	
	headers = { "Authorization" : "Bearer "+ACCESS_TOKEN,
				"Accept" : "application/json",
				"Content-Type" : "application/json"}

	load_on_b3na = requests.put(url, \
				 data=json.dumps(values), \
				 headers=headers)

	if load_on_b3na.status_code == requests.codes.ok or load_on_b3na.status_code == 204:
		logger.info("Successfully loaded Spotify on B3na")
	else:
		logger.error("Failed to load Spotify on B3na")
		logger.error("Error code: "+str(load_on_b3na.status_code))
		try:
			logger.error("Error json: "+str(load_on_b3na.json()))
		except:
			logger.error("Unable to get more error details")
		return

	logger.info("Starting Spotify playback")
	# RED LIGHTING SPOTIFY PLAYLIST:
	# spotify:user:1249844952:playlist:4F2fAhORzNTtvBL2FOtGqR
	# ON THE ROAD PLAYLIST
	# spotify:user:22q2mipzh23ikceoixqzozv6q:playlist:2Fakjp8KmV37Mri7fYr0rR
	url = 'https://api.spotify.com/v1/me/player/play'
	values = { 'context_uri': 'spotify:user:22q2mipzh23ikceoixqzozv6q:playlist:2Fakjp8KmV37Mri7fYr0rR'}
	headers = { "Authorization" : "Bearer "+ACCESS_TOKEN,
				"Accept" : "application/json",
				"Content-Type" : "application/json"}

	play_on_b3na = requests.put(url, \
				 data=json.dumps(values), \
				 headers=headers)
	if play_on_b3na.status_code == requests.codes.ok or play_on_b3na.status_code == 204:
		logger.info("Successfully started Spotify playback")
	else:
		logger.error("Failed to start Spotify playback on B3na")
		logger.error("Error code: "+str(play_on_b3na.status_code))
		try:
			logger.error("Error json: "+str(play_on_b3na.json()))
		except:
			logger.error("Unable to get more error details")
		return

# Main - only really used for testing
if __name__ == '__main__':
	main()