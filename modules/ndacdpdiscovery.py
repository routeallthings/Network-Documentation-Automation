#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# ndacdpdiscovery.py

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
from addressinnetwork import *

# Get root path and add macdb library and template library
import inspect, os.path, sys
filename = inspect.getframeinfo(inspect.currentframe()).filename
cdprootpath = os.path.dirname(os.path.abspath(filename))
# MAC OUI Library
cdprpath,lastfolder = os.path.split(cdprootpath)
lastfolder = 'macdb'
macdbpath = os.path.join(cdprpath,lastfolder)
# Template Library
cdprpath,lastfolder = os.path.split(cdprootpath)
lastfolder = 'templates'
templatepath = os.path.join(cdprpath,lastfolder)

def cdpdiscovery(usernamelist,cdpseedv,cdpdevicetypev,cdpdiscoverydepthv,includedsubnets,excludedsubnets):
	cdpdevicecomplete = []
	cdpdevicetemp = []
	cdpduplicateip = []
	cdpduplicatehostname = []
	tempfilelist = []
	# Create Commands
	showcdp = "show cdp neighbor detail"
	# Duplicate IP Detection (Add Core)
	cdpduplicateip.append(cdpseedv)
	# FSM Templates
	if "cisco_ios" in cdpdevicetypev.lower():
		templatename = "cisco_ios_show_cdp_nei_detail.template"
	if "cisco_xe" in cdpdevicetypev.lower():
		templatename = "cisco_ios_show_cdp_nei_detail.template"
	if "cisco_nxos" in cdpdevicetypev.lower():
		templatename = "cisco_nxos_show_cdp_nei_detail.template"
	# Create template file path
	templatefile = os.path.join(templatepath,templatename)
	# Open and store in memory
	with open(templatefile, 'r') as fsmtemplatenamefile:
		fsmcdptemplate = textfsm.TextFSM(fsmtemplatenamefile)
	#
	sshdevicetype = cdpdevicetypev
	sshdeviceip = cdpseedv
	# First Level of Discovery and building the initial seed discovery
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
	except NameError:
		print 'Could not successfully connect to the CDP seed device at ' + cdpseedv +'.'
		time.sleep(5)
		sys.exit()
	except Exception as e:
		print 'Error while gathering data on ' + cdpseedv + '. Error is ' + str(e)
		time.sleep(5)
		sys.exit()
	sshdevicehostname = sshnet_connect.find_prompt()
	sshdevicehostname = sshdevicehostname.strip('#')
	if '>' in sshdevicehostname:
		sshnet_connect.enable()
		sshdevicehostname = sshdevicehostname.strip('>')
		sshdevicehostname = sshnet_connect.find_prompt()
		sshdevicehostname = sshdevicehostname.strip('#')
	print 'CDP discovery starting on seed device ' + sshdevicehostname + ' (' + cdpseedv + ')'
	# Duplicate Hostname Detection
	cdpduplicatehostname.append(sshdevicehostname)
	# Continue
	sshcommand = showcdp
	sshresult = sshnet_connect.send_command(sshcommand)
	hcshowcdp = fsmcdptemplate.ParseText(sshresult)
	print 'Attempting discovery on the seed router'
	# Adding Seed Router to reports
	seedroutertype = re.search('(\S+)_(\S+)',sshdevicetype)
	cdpdevicedict = {}
	cdpdevicedict['Device IPs'] = sshdeviceip
	cdpdevicedict['Vendor'] = seedroutertype.group(1)
	cdpdevicedict['Type'] = seedroutertype.group(2)
	cdpdevicecomplete.append(cdpdevicedict)
	# Starting loop
	for cdpnei in hcshowcdp:
		try:	
			cdpalreadyexists = 0
			cdpnexthop = 0
			cdpdevicedict = {}
			cdpneiname = cdpnei[0]
			cdpneiip = cdpnei[1]
			cdpneidevice = cdpnei[2]
			cdpneiosfull = cdpnei[5]
			subnetcheck = 0
			subnetcheck2 = 0
			if cdpneiip == None or cdpneiip == '':
				subnetcheck2 = 0
			else:
				subnetcheck2 = 1
			if subnetcheck2 == 1:
				for subnetwork in includedsubnets:
						if addressinnetwork(cdpneiip,subnetwork) == True:
							subnetcheck = 1
			if subnetcheck2 == 1:
				for subnetwork in excludedsubnets:
						if addressinnetwork(sshdeviceip,subnetwork) == True:
							subnetcheck = 0
			if subnetcheck == 1:
				if 'cisco' in cdpneidevice.lower() or 'cisco' in cdpneiosfull.lower():
					cdpneivend = 'cisco'
					if re.match('.*\iosxe|xe.*',cdpneiosfull.lower()):
						cdpneios = 'xe'
						cdpnexthop = 1
					if re.match('.*ios(?!xe).*',cdpneiosfull.lower()):
						cdpneios = 'ios'
						cdpnexthop = 1
					if re.match('.*nx-os|nexus.*',cdpneiosfull.lower()):
						cdpneios = 'nxos'
						cdpnexthop = 1
					for cdpdevice in cdpdevicetemp:
						cdpdeviceip = cdpdevice.get('Device IPs').encode('utf-8')
						if cdpdeviceip == cdpneiip:
							cdpalreadyexists = 1
					if cdpalreadyexists == 0 and cdpnexthop == 1:
						cdpdevicedict['Device IPs'] = cdpneiip.decode('utf-8')
						cdpdevicedict['Vendor'] = cdpneivend.decode('utf-8')
						cdpdevicedict['Type'] = cdpneios.decode('utf-8')
						cdpdevicetemp.append(cdpdevicedict)
		except IndexError:
			print 'Could not connect to device ' + cdpneiip
			try:
				sshnet_connect.disconnect()
			except:
				pass
		except Exception as e:
			print 'Error with collecting CDP data on ' + cdpneiip + '. Error is ' + str(e)
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
		
	# Attempt Subsequent Discovery Levels (Non-Threaded)
	def cdpdiscoverysub(usernamelist,sshdeviceip,cdptype,cdpvendor,cdpdiscoverydepthv,includedsubnets,excludedsubnets):
		try:
			# Duplicate IP Detection
			for dupip in cdpduplicateip:
				if dupip == sshdeviceip:
					return
			cdpduplicateip.append(sshdeviceip)
			# Continue			
			subnetcheck = 0
			subnetcheck2 = 0
			if sshdeviceip == None or sshdeviceip == '':
				subnetcheck2 = 0
			else:
				subnetcheck2 = 1
			if subnetcheck2 == 1:
				for subnetwork in includedsubnets:
						if addressinnetwork(sshdeviceip,subnetwork) == True:
							subnetcheck = 1
			if subnetcheck2 == 1:
				for subnetwork in excludedsubnets:
						if addressinnetwork(sshdeviceip,subnetwork) == True:
							subnetcheck = 0
			# FSM Templates
			if subnetcheck == 1:
				cdpdevicetype = cdpvendor.lower() + '_' + cdptype.lower()
				if "cisco_ios" in cdpdevicetypev.lower():
					templatename = "cisco_ios_show_cdp_nei_detail.template"
				if "cisco_xe" in cdpdevicetypev.lower():
					templatename = "cisco_ios_show_cdp_nei_detail.template"
				if "cisco_nxos" in cdpdevicetypev.lower():
					templatename = "cisco_nxos_show_cdp_nei_detail.template"
				# Create template file path
				templatefile = os.path.join(templatepath,templatename)
				# Open and store in memory
				with open(templatefile, 'r') as fsmtemplatenamefile:
					fsmcdptemplate = textfsm.TextFSM(fsmtemplatenamefile)
				# CDP Check
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
							sshnet_connect = ConnectHandler(device_type=sshdevicetype, ip=sshdeviceip, username=sshusername, password=sshpassword, secret=enablesecret, timeout=3)
							break
						except Exception as e:
							if 'Authentication' in e:
								continue
							else:
								sshdevicetypetelnet = sshdevicetype + '_telnet'
								try:
									sshnet_connect = ConnectHandler(device_type=sshdevicetypetelnet, ip=sshdeviceip, username=sshusername, password=sshpassword, secret=enablesecret, timeout=3)
									break
								except:
									continue
				except:
					pass
				skipcheck = 0
				try:
					sshnet_connect
					skipcheck = 0
				except:
					print 'Error with connecting to ' + sshdeviceip
					skipcheck = 1
				if skipcheck == 0:
					sshdevicehostname = sshnet_connect.find_prompt()
					sshdevicehostname = sshdevicehostname.strip('#')
					if '>' in sshdevicehostname:
						sshnet_connect.enable()
						sshdevicehostname = sshdevicehostname.strip('>')
						sshdevicehostname = sshnet_connect.find_prompt()
						sshdevicehostname = sshdevicehostname.strip('#')
					# Duplicate Hostname Detection
					for hostname in cdpduplicatehostname:
						if hostname == sshdevicehostname:
							sshnet_connect.disconnect()
							return
					cdpduplicatehostname.append(sshdevicehostname)
					print 'CDP discovery starting on secondary device ' + sshdevicehostname + ' (' + sshdeviceip + ')'
					# Adding to master list
					cdpdevicedict = {}
					cdpdevicedict['Device IPs'] = sshdeviceip
					cdpdevicedict['Vendor'] = cdpvendor
					cdpdevicedict['Type'] = cdptype
					cdpdevicecomplete.append(cdpdevicedict)
					# Show Interfaces
					sshcommand = showcdp
					sshresult = sshnet_connect.send_command(sshcommand)
					hcshowcdp = fsmcdptemplate.ParseText(sshresult)
					for cdpnei in hcshowcdp:
						cdpalreadyexists = 0
						cdpnexthop = 0
						cdpdevicedict = {}
						cdpneiname = cdpnei[0]
						cdpneiip = cdpnei[1]
						cdpneidevice = cdpnei[2]
						cdpneiosfull = cdpnei[5]
						if 'cisco' in cdpneidevice.lower():
							cdpneivend = 'cisco'
							if re.match('.*\iosxe|xe.*',cdpneiosfull.lower()):
								cdpneios = 'xe'
								cdpnexthop = 1
							if re.match('.*ios(?!xe).*',cdpneiosfull.lower()):
								cdpneios = 'ios'
								cdpnexthop = 1
							if re.match('.*nx-os|nexus.*',cdpneiosfull.lower()):
								cdpneios = 'nxos'
								cdpnexthop = 1
							for cdpdevice in cdpdevicetemp:
								cdpdeviceip = cdpdevice.get('Device IPs').encode('utf-8')
								if cdpdeviceip == cdpneiip:
									cdpalreadyexists = 1
							if cdpalreadyexists == 0 and cdpnexthop == 1:
								cdpdevicedict['Device IPs'] = cdpneiip.decode('utf-8')
								cdpdevicedict['Vendor'] = cdpneivend.decode('utf-8')
								cdpdevicedict['Type'] = cdpneios.decode('utf-8')
								cdpdevicetemp.append(cdpdevicedict)
								print 'Found new device, adding to list'
		except IndexError:
			print 'Could not connect to device ' + sshdeviceip
			try:
				sshnet_connect.disconnect()
			except:
				pass
		except Exception as e:
			print 'Error with collecting CDP data on ' + cdpip + '. Error is ' + str(e)
			cdpdevicediscovery.append(cdpip.decode('utf-8'))
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
	# Start CDP Discovery
	cdpdiscoverydepthv = 30
	cdpmaxloop = cdpdiscoverydepthv * 3
	cdpmaxloopiteration = 0
	if not cdpdevicetemp == []:
		while cdpmaxloopiteration < cdpmaxloop:
			for cdpdevice in cdpdevicetemp:
				cdpdupdetect=0
				cdpip = cdpdevice.get('Device IPs').encode('utf-8')
				for cdpdup in cdpduplicateip:
					if cdpip == cdpdup:
						cdpdupdetect = 1
				cdpvendor = cdpdevice.get('Vendor').encode('utf-8')
				cdptype = cdpdevice.get('Type').encode('utf-8')
				if not cdpdupdetect == 1:
					cdpdiscoverysub(usernamelist,cdpip,cdptype,cdpvendor,cdpdiscoverydepthv,includedsubnets,excludedsubnets)
				cdpmaxloopiteration = cdpmaxloopiteration + 1
	try:
		for file in tempfilelist:
			try:
				os.remove(file)
			except:
				pass
	except:
		pass
	print '###################################################'
	print 'Completed CDP Discovery, starting additional tasks'
	print '###################################################'
	return cdpdevicecomplete 