#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# addressInNetwork.py

# Native Modules
import os

# Non-Native Modules
# netaddr
try:
	from netaddr import IPNetwork, IPAddress
except ImportError:
	netaddrinstallstatus = raw_input ('netaddr module is missing, would you like to automatically install? (Y/N): ')
	if 'y' in netaddrinstallstatus.lower():
		os.system('python -m pip install netaddr')
		from netaddr import IPNetwork, IPAddress
	else:
		print 'You selected an option other than yes. Please be aware that this script requires the use of netaddr. Please install manually and retry'
		print 'Exiting in 5 seconds'
		time.sleep(5)
		sys.exit()

def addressinnetwork(ip,net):
	"Is an address in a network"
	if IPAddress(ip) in IPNetwork(net):
		return True
	else:
		return False