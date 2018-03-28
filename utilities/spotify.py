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
import json
import base64
import logging
import urllib
import urllib2
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
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))

#=====================================
# Account Config Stuff
#=====================================
CLIENT_ID = os.environ.get("SPOTIFY_CLID") or config.get("Spotify","id")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLSEC") or config.get("Spotify","secret")
USERNAME = os.environ.get("SPOTIFY_USERNAME") or config.get("Spotify","username")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT") or config.get("Spotify","redirect_uri")
ACCESS_TOKEN = os.environ.get("SPOTIFY_ACCESS_TOKEN") or config.get("Spotify","access_token")
REFRESH_TOKEN = os.environ.get("SPOTIFY_REFRESH_TOKEN") or config.get("Spotify","refresh_token")
SCOPE='user-library-read streaming user-read-playback-state'
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
	print 'init'

	os.environ["SPOTIPY_CLIENT_ID"] = CLIENT_ID
	os.environ["SPOTIPY_CLIENT_SECRET"] = CLIENT_SECRET
	os.environ["SPOTIPY_REDIRECT_URI"] = REDIRECT_URI

	#======================================
	# Step 0: Authorize app
	#======================================
	# TODO: this is tricky because it caches the token in random location... 
	# gotta find a workaround.
	token = sp_util.prompt_for_user_token(username=USERNAME, scope=SCOPE)

	print 'init end'
	return token
		

def main():
	print 'main'

	refresh_token()

	device = find_device()

	b3na_play(device=device)

	print 'end main'


#======================================
# Step 1: Request New Access Token
#======================================
def refresh_token():
	print "REQUESTING NEW TOKEN"
	url = 'https://accounts.spotify.com/api/token'
	values = {'grant_type' : 'refresh_token',
	          'refresh_token' : REFRESH_TOKEN }
	headers = { "Authorization" : "Basic "+str(KEY64) }

	data = urllib.urlencode(values)
	data = data.encode('ascii')
	req = urllib2.Request(url, data, headers)
	print (url, data, headers)
	try:
		response = urllib2.urlopen(req)
		the_page = response.read()	
		ret_data = json.loads(the_page)
		print ret_data
		print "new access_token", ret_data['access_token']
		config.set('Spotify','access_token',ret_data['access_token'])

		global ACCESS_TOKEN
		ACCESS_TOKEN = ret_data['access_token']
	except Exception, e:
		print "ERROR getting access token. Giving up"
		print "Traceback: "+str(e)
		return

#======================================
# Step 2: Get list of devices
#======================================	
def find_device():
	print "REQUESTING LIST OF DEVICES"
	url = 'https://api.spotify.com/v1/me/player/devices'
	headers = { "Authorization" : "Bearer "+ACCESS_TOKEN }

	req = urllib2.Request(url, headers=headers)
	print (url, headers)
	response = urllib2.urlopen(req)
	the_page = response.read()	
	ret_data = json.loads(the_page)

	device = None
	for dev in ret_data['devices']:
		print dev['name']
		#if dev['name'] == "B3na":
		if dev['name'] == "Shogun":    #DEBUG
			print "B3na found"
			device = dev
			break

	if not device:
		print "B3NA NOT FOUND"
		return
	else:
		print device

	return device

#======================================
# Step 3: Play on B3na
#======================================	
def b3na_play(device):
	print "PLAYING ON B3NA"
	url = 'https://api.spotify.com/v1/me/player'
	values = {'device_ids' : device['id']}	

	headers = { "Authorization" : "Bearer "+ACCESS_TOKEN,
				"Accept" : "application/json",
				"Content-Type" : "application/json"}

	req = urllib2.Request(url, headers=headers)
	print (url, headers)
	response = urllib2.urlopen(req)
	the_page = response.read()	
	print the_page
	ret_data = json.loads(the_page)	

# Main - only really used for testing
if __name__ == '__main__':
	main()