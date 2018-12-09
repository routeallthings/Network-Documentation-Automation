#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# ndahealthcheck.py

# Import Modules
# Native
import sys
import os
# NetMiko
import netmiko
from netmiko import ConnectHandler
from paramiko.ssh_exception import SSHException 
from netmiko.ssh_exception import NetMikoTimeoutException
# TextFSM
import textfsm
# NDA
from ndacommands import *
from downloadfile import *

# Get root path and add macdb library and template library
import inspect, os.path, sys
filename = inspect.getframeinfo(inspect.currentframe()).filename
hcrootpath = os.path.dirname(os.path.abspath(filename))
# MAC OUI Library
hcrpath,lastfolder = os.path.split(hcrootpath)
lastfolder = 'macdb'
macdbpath = os.path.join(hcrpath,lastfolder)
# Template Library
hcrpath,lastfolder = os.path.split(hcrootpath)
lastfolder = 'templates'
templatepath = os.path.join(hcrpath,lastfolder)

def healthcheck(sshdevice,usernamelist,exportlocation):
	# Definition Variables
	tempfilelist = []
	healthchecklist = []
	# Start
	sshdeviceip = sshdevice.get('Device IPs').encode('utf-8')
	sshdevicevendor = sshdevice.get('Vendor').encode('utf-8')
	sshdevicetype = sshdevice.get('Type').encode('utf-8')
	sshdevicetype = sshdevicevendor.lower() + "_" + sshdevicetype.lower()
	### FSM Templates ###
	# FSM Show Interface
	if "cisco_ios" in sshdevicetype:
		templatename = "cisco_ios_show_interfaces_health.template"
	if "cisco_xe" in sshdevicetype:
		templatename = "cisco_ios_show_interfaces_health.template"
	if "cisco_nxos" in sshdevicetype:
		templatename = "cisco_nxos_show_interfaces_health.template"
	# Create template file path
	templatefile = os.path.join(templatepath,templatename)
	# Open and convert to TextFSM
	with open(templatefile, 'r') as fsmtemplatenamefile:
		fsminttemplate = textfsm.TextFSM(fsmtemplatenamefile)
	# FSM Show Temperature
	if "cisco_ios" in sshdevicetype:
		templatename = "cisco_ios_show_temp_health.template"
	if "cisco_xe" in sshdevicetype:
		templatename = "cisco_ios_show_temp_health.template"
	if "cisco_nxos" in sshdevicetype:
		templatename = "cisco_nxos_show_temp_health.template"	
	# Create template file path
	templatefile = os.path.join(templatepath,templatename)
	# Open and store in memory
	with open(templatefile, 'r') as fsmtemplatenamefile:
		fsmtemptemplate = textfsm.TextFSM(fsmtemplatenamefile)
	#Start Connection
	try:
		for username in usernamelist:
			try:
				sshusername = username.get('sshusername').encode('utf-8')
				sshpassword = username.get('sshpassword').encode('utf-8')
				enablesecret = username.get('enablesecret').encode('utf-8')
			except:
				sshusername = username.get('sshusername')
				sshpassword = username.get('sshpassword')
				enablesecret = username.get('enablesecret')
			try:
				sshnet_connect = ConnectHandler(device_type=sshdevicetype, ip=sshdeviceip, username=sshusername, password=sshpassword, secret=enablesecret)
				break
			except Exception as e:
				if 'Authentication' in e:
					continue
				else:
					sshdevicetypetelnet = sshdevicetype + '_telnet'
					try:
						sshnet_connect = ConnectHandler(device_type=sshdevicetypetelnet, ip=sshdeviceip, username=sshusername, password=sshpassword, secret=enablesecret)
						break
					except:
						continue
		try:
			sshnet_connect
		except:
			print 'Error with connecting to ' + sshdeviceip
			sys.exit()
		sshdevicehostname = sshnet_connect.find_prompt()
		sshdevicehostname = sshdevicehostname.strip('#')
		if '>' in sshdevicehostname:
			sshnet_connect.enable()
			sshdevicehostname = sshdevicehostname.strip('>')
			sshdevicehostname = sshnet_connect.find_prompt()
			sshdevicehostname = sshdevicehostname.strip('#')
		print 'Health Check starting on ' + sshdevicehostname
		#Show Interfaces
		sshcommand = showinterface
		sshresult = sshnet_connect.send_command(sshcommand)
		hcshowint = fsminttemplate.ParseText(sshresult)
		#Parse through each interface looking for issues
		healthcheckcsv = []
		for hcshowintsingle in hcshowint:
			hcinterfacename = hcshowintsingle[0].encode('utf-8')
			if not 'notconnect' in hcshowintsingle[2]:
				# Look for duplexing issues
				if 'Half-duplex' in hcshowintsingle[6]:
					hcerror = 'Duplex Mismatch'
					hcdescription = hcinterfacename + ' is showing as half-duplex. If this is by design please ignore.'
					healthcheckcsv.append ((sshdevicehostname + ',' + hcerror + ',' + hcdescription))
				if '10Mb/s' in hcshowintsingle[7]:
					hcerror = 'Duplex Mismatch'
					hcdescription = hcinterfacename + ' is showing as 10Mb/s. If this is by design please ignore.'
					healthcheckcsv.append ((sshdevicehostname + ',' + hcerror + ',' + hcdescription))
				# Look for interface counter errors
				# Input Errors
				hcshowintsingleint = hcshowintsingle[8]
				if hcshowintsingleint == '':
					hcshowintsingleint = 0
				hcshowintsingleint = int(hcshowintsingleint)
				if hcshowintsingleint > 20:
					hcerror = 'Input Errors'
					hcinterfacecounter = hcshowintsingle[8]
					hcinterfacecounter = hcinterfacecounter.encode('utf-8')
					hcdescription = hcinterfacename + ' is showing ' + hcinterfacecounter + ' input errors. Usually indicative of a bad link (cabling and/or optic failure).'
					healthcheckcsv.append ((sshdevicehostname + ',' + hcerror + ',' + hcdescription))
				# CRC errors
				hcshowintsingleint = hcshowintsingle[9]
				if hcshowintsingleint == '':
					hcshowintsingleint = 0
				hcshowintsingleint = int(hcshowintsingleint)			
				if hcshowintsingleint > 20:
					hcerror = 'CRC Errors'
					hcinterfacecounter = hcshowintsingle[9]
					hcinterfacecounter = hcinterfacecounter
					hcinterfacecounter = hcinterfacecounter.encode('utf-8')
					hcdescription = hcinterfacename + ' is showing ' + hcinterfacecounter + ' CRC errors. Usually indicative of incorrect duplexing settings or a bad link (cabling and/or optic failure).'
					healthcheckcsv.append ((sshdevicehostname + ',' + hcerror + ',' + hcdescription))
				# Output errors
				hcshowintsingleint = hcshowintsingle[10]
				if hcshowintsingleint == '':
					hcshowintsingleint = 0
				hcshowintsingleint = int(hcshowintsingleint)		
				if hcshowintsingleint > 100:
					hcerror = 'Saturated Link'
					hcinterfacecounter = hcshowintsingle[10]
					hcinterfacecounter = hcinterfacecounter.encode('utf-8')
					hcdescription = hcinterfacename + ' is showing ' + hcinterfacecounter + ' output errors. This is usually indicative of a saturated interface.  '
					healthcheckcsv.append ((sshdevicehostname + ',' + hcerror + ',' + hcdescription))
				# Collisions
				hcshowintsingleint = hcshowintsingle[11]
				if hcshowintsingleint == '':
					hcshowintsingleint = 0
				hcshowintsingleint = int(hcshowintsingleint)
				if hcshowintsingleint > 20:
					hcerror = 'Shared Medium'
					hcinterfacecounter = hcshowintsingle[11]
					hcinterfacecounter = hcinterfacecounter.encode('utf-8')
					hcdescription = hcinterfacename + ' is showing ' + hcinterfacecounter + ' collisions.  '
					healthcheckcsv.append ((sshdevicehostname + ',' + hcerror + ',' + hcdescription))		
				# Interface resets
				hcshowintsingleint = hcshowintsingle[12]
				if hcshowintsingleint == '':
					hcshowintsingleint = 0
				hcshowintsingleint = int(hcshowintsingleint)			
				if hcshowintsingleint > 20:
					hcerror = 'Interface Reset Count'
					hcinterfacecounter = hcshowintsingle[12]
					hcinterfacecounter = hcinterfacecounter.encode('utf-8')
					hcdescription = hcinterfacename + ' is showing ' + hcinterfacecounter + ' interface resets. '
					healthcheckcsv.append ((sshdevicehostname + ',' + hcerror + ',' + hcdescription))
		#Show Temperature
		try:
			if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
				sshcommand = showtemp
				sshresult = sshnet_connect.send_command(sshcommand)
				hcshowtemp = fsmtemptemplate.ParseText(sshresult)
				hctempdegrees = hcshowtemp[0]
				hctempdegrees = hctempdegrees[0]
				hctempdegrees = hctempdegrees.encode('utf-8')
				hctempdegreesint = int(hctempdegrees)
				if hctempdegreesint > 45:
					hcerror = 'Temperature Alert'
					hcdescription = 'Temperature has been recorded at ' + hctempdegrees + ' Celsius. Please lower the temperature for the surrounding environment '
					healthcheckcsv.append ((sshdevicehostname + ',' + hcerror + ',' + hcdescription))
			if 'cisco_nxos' in sshdevicetype.lower():
				sshcommand = showtemp_nxos
				sshresult = sshnet_connect.send_command(sshcommand)
				hcshowtemp = fsmtemptemplate.ParseText(sshresult)
				hctempdegrees = hcshowtemp[0]
				hctempdegrees = hctempdegrees[0]
				hctempdegrees = hctempdegrees.encode('utf-8')
				hctempdegreesint = int(hctempdegrees)
				if hctempdegreesint > 45:
					hcerror = 'Temperature Alert'
					hcdescription = 'Temperature has been recorded at ' + hctempdegrees + ' Celsius. Please lower the temperature for the surrounding environment '
					healthcheckcsv.append ((sshdevicehostname + ',' + hcerror + ',' + hcdescription))
		except:
			pass
		# Exit SSH
		sshnet_connect.disconnect()
		# Parse list into dictionary/list
		saveresultslistsplit = []
		for saveresultsrow in healthcheckcsv:
			saveresultslistsplit.append(saveresultsrow.strip().split(','))
		saveresultslistsplit = [saveresultslistsplit[i:i+3] for i in range(0,len(saveresultslistsplit),3)]
		for saveresultsplitrow in saveresultslistsplit:
			for saveresultssplitrow2 in saveresultsplitrow:
				tempdict = {}
				tempdict['Hostname'] = saveresultssplitrow2[:1][0]
				tempdict['Error'] = saveresultssplitrow2[1:][0]
				tempdict['Description'] = saveresultssplitrow2[2:][0]
				healthchecklist.append(tempdict)
	except IndexError:
		print 'Could not connect to device ' + sshdeviceip
		try:
			sshnet_connect.disconnect()
		except:
			pass
	except Exception as e:
		print 'Error while running health check with ' + sshdeviceip + '. Error is ' + str(e)
		try:
			sshnet_connect.disconnect()
		except:
			pass
	except KeyboardInterrupt:
		print 'CTRL-C pressed, exiting script'
		try:
			sshnet_connect.disconnect()
		except:
			pass
	print 'Completed health check for ' + sshdeviceip
	try:
		for file in tempfilelist:
			try:
				os.remove(file)
			except:
				pass
	except:
		pass
	return healthchecklist