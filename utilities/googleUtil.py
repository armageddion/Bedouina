#!/usr/bin/python

"""
This is a utility for all Google APIs - gmail, calendar..
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

from __future__ import print_function
import os
import time
import datetime
import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from apiclient import discovery
from oauth2client import client
from oauth2client import tools

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES_GMAIL = 'https://www.googleapis.com/auth/gmail.readonly'
SCOPES_CAL = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE_GMAIL = os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),'../conf/client_secret_gmail.json')
CLIENT_SECRET_FILE_CAL = os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),'../conf/client_secret_calendar.json')
APPLICATION_NAME = 'Alfr3d'

# calculate offset to UTC
#timezone_offset = "-04:00"
timezone_offset = "Z"
tz_off = datetime.datetime.now().hour-datetime.datetime.utcnow().hour
if tz_off < 0:
	timezone_offset = str(tz_off).zfill(3)+":00"
else:
	timezone_offset = "+"+str(tz_off).zfill(2)+":00"

def get_credentials_gmail():
	"""Gets valid user credentials from storage.

	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.

	Returns:
		Credentials, the obtained credential.
	"""
	home_dir = os.path.expanduser('~')
	# credential_dir = os.path.join(home_dir, '.credentials')
	credential_dir = os.path.join(os.path.dirname(__file__),'../conf')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,
								   'gmail.storage')
	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE_GMAIL, SCOPES_GMAIL)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	return credentials

def get_credentials_cal():
	"""Gets valid user credentials from storage.

	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.

	Returns:
		Credentials, the obtained credential.
	"""
	home_dir = os.path.expanduser('~')
	# credential_dir = os.path.join(home_dir, '.credentials')
	credential_dir = os.path.join(os.path.dirname(__file__),'../conf')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,
								   'calendar.storage')
	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE_CAL, SCOPES_CAL)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	return credentials    

def getUnreadCount():
	"""
		Description:
			This function provides the count of unread messages in my gmail inbox 
		Returns:
			Intiger value of under emails
	"""
	credentials = get_credentials_gmail()

	# Authorize the httplib2.Http object with our credentials
	http = credentials.authorize(httplib2.Http())

	# Build the Gmail service from discovery
	gmail_service = discovery.build('gmail', 'v1', http=http)

	messages = gmail_service.users().messages().list(userId='me', q='label:inbox is:unread').execute()
	unread_msgs = messages[u'resultSizeEstimate']

	return unread_msgs

def calendarTomorrow():   
	credentials = get_credentials_cal()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar', 'v3', http=http)

	tomorrow = datetime.datetime.now().replace(hour=0,minute=0) + datetime.timedelta(days=1)
	tomorrow_night = tomorrow + datetime.timedelta(hours=23, minutes=59)
	tomorrow = tomorrow.isoformat()+timezone_offset
	tomorrow_night = tomorrow_night.isoformat()+timezone_offset
	
	print('Getting the first event of tomorrow')
	eventsResult = service.events().list(
		calendarId='primary', timeMin=tomorrow, maxResults=1, timeMax=tomorrow_night, singleEvents=True,
		orderBy='startTime').execute()
	events = eventsResult.get('items', [])

	if not events:
		print('No upcoming events found.')
	else:
		return events[0]

	# for event in events:
	# 	start = event['start'].get('dateTime', event['start'].get('date'))
	# 	print(start, event['summary']) 

	# 	# since there is only one event, we're ok to do this
	# 	return event

def calendarToday():
	credentials = get_credentials_cal()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar', 'v3', http=http)

	today = datetime.datetime.now()
	tonight = datetime.datetime.now().replace(hour=23,minute=59)
	today = today.isoformat()+timezone_offset
	tonight = tonight.isoformat()+timezone_offset
	
	print('Getting todays events')
	eventsResult = service.events().list(
		calendarId='primary', timeMin=today, maxResults=10, timeMax=tonight, singleEvents=True,
		orderBy='startTime').execute()
	events = eventsResult.get('items', [])

	if not events:
		print('No upcoming events found.')
		return None

	# for event in events:
	# 	start = event['start'].get('dateTime', event['start'].get('date'))
	# 	print(start, event['summary']) 

	return events

# Main
if __name__ == '__main__':
	print("this is alfr3ds google utility")

