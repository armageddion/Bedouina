import os

from app import app, db
from app.models import Device

netclientsfile = "netclients.tmp"

os.system("sudo arp-scan --localnet > "+netclientsfile)

netClients = open(netclientsfile, 'r')

netClientsMACs = []
netClientsIPs = []
netClientsHosts = []

for line in netClients:
	ret = line.split('\t')
	ret2 = ret[0].split('.')
	if ret2[0] == ('10') and ret2[1] == ('0'):
		netClientsMACs.append(ret[1])
		netClientsIPs.append(ret[0])

netClients2 = {}
for i in range(len(netClientsMACs)):
	#add everything into database
	d = Device(name='unknown',
			   IP=netClientsIPs[i],
			   MAC=netClientsMACs[i])

	print ("\nAdding device:")
	print ("================")
	print ("  IP = ",netClientsIPs[i])
	print ("  MAC = ", netClientsMACs[i])

	db.session.add(d)
	db.session.commit()
