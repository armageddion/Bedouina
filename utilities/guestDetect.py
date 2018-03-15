#!/usr/bin/python

"""
	This is a utility for detecting clients on Alfr3d LAN and
	storing new guests into the existing database
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
import ConfigParser
import time
import socket
import logging
from datetime import datetime
from pymongo import MongoClient
from time import strftime, localtime, time

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging
logger = logging.getLogger("NetworkLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/localnet.log"))
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

def checkLANMembers():
	"""
		Description:
			This function checks who is on LAN
	"""
	logger.info("Checking localnet for online devices")

	# set up configuration and temporary files
	# config file for daemon specific configs
	configFile = (os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),'../conf/alfr3ddaemon.conf'))
	# temporary file for storing results of network scan
	netclientsfile = os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),'../log/netclients.tmp')
	# temporary file for secondary network scan
	nethostsfile = os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),'../log/nethosts.tmp')

	# depending on where the daemon is running....
	# find out who is online
	if socket.gethostname() == 'psamathe':
		#os.system("sudo arp-scan --interface=p1p1 --localnet > "+ netclientsfile)	#PSAMATHE
		os.system("sudo arp-scan --localnet > "+ netclientsfile)	#PSAMATHE
	else:
		os.system("sudo arp-scan --localnet > "+ netclientsfile)

	netClients = open(netclientsfile, 'r')
	netClientsMACs = []
	netClientsIPs = []
	netClientsHosts = []

	# Parse MAC and IP addresses (depending on host)
	if socket.gethostname() == 'psamathe':
		for line in netClients:
			ret = line.split('\t')
			ret2 = ret[0].split('.')
			if ret2[0] == ('192') and ret2[1] == ('168'):
				print ret[0]
				# parse MAC addresses from arp-scan run
				netClientsMACs.append(ret[1])
				# parse IP addresses from arp-scan run
				netClientsIPs.append(ret[0])
	else:
		for line in netClients:
			ret = line.split('\t')
			ret2 = ret[0].split('.')
			if ret2[0] == ('10') and ret2[1] == ('0'):
				# parse MAC addresses from arp-scan run
				netClientsMACs.append(ret[1])
				# parse IP addresses from arp-scan run
				netClientsIPs.append(ret[0])
			elif ret2[0] == ('192') and ret2[1] == ('168'):
				# parse MAC addresses from arp-scan run
				netClientsMACs.append(ret[1])
				# parse IP addresses from arp-scan run
				netClientsIPs.append(ret[0])

	# clean up and parse MAC&IP info
	netClients2 = {}
	for i in range(len(netClientsMACs)):
		netClients2[netClientsMACs[i]] = netClientsIPs[i]

	# find who is online and
	# update DB status and last_online time
	for member in netClientsMACs:
		device = Device()
		exists = device.getDevice(member)

		#if device exists in the DB update it
		if exists:
			logger.info("Updating device with MAC: "+member)
			device.IP = netClients2[member]
			device.update()

		#otherwise, create and add it. 
		else:
			logger.info("Creating a new DB entry for device with MAC: "+member)
			device.IP = netClients2[member]
			device.MAC = member
			device.newDevice(member)	

	# logger.info("Updating users")
	# user = User()
	# user.refreshAll()
	logger.info("Updating devices")
	device = Device()
	device.refreshAll()

	logger.info("Cleaning up temporary files")
	os.system('rm -rf '+netclientsfile)
	os.system('rm -rf '+nethostsfile)


# Main - only really used for testing
if __name__ == '__main__':
	checkLANMembers()
