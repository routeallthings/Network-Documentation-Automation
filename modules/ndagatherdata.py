#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# ndagatherdata.py

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
# Download file from toolkit
from downloadfile import *
from removeprefix import *

# Get root path and add macdb library and template library
import inspect, os.path, sys
filename = inspect.getframeinfo(inspect.currentframe()).filename
gdrootpath = os.path.dirname(os.path.abspath(filename))
# MAC OUI Library
gdrpath,lastfolder = os.path.split(gdrootpath)
lastfolder = 'macdb'
macdbpath = os.path.join(gdrpath,lastfolder)
# Template Library
gdrpath,lastfolder = os.path.split(gdrootpath)
lastfolder = 'templates'
templatepath = os.path.join(gdrpath,lastfolder)

def writeoutput(sshcommand,sshresult,sshdevicehostname,outputfolder):
	sshcommandfile = sshcommand.replace(' ','')
	sshcommandfile = sshcommandfile.replace('-','')
	outputfile = outputfolder + '\\' + sshdevicehostname + '_' + sshcommandfile + '.txt'
	f = open(outputfile,'w')
	f.write(sshresult)
	f.close()

def gatherdata(sshdevice,usernamelist,exportlocation):
	# Definition Variables
	tempfilelist = []
	fullinventorylist = []
	ipmactablelist = []
	mactablelist = []
	iparptablelist = []
	l2interfacelist = []
	l3interfacelist = []
	poeinterfacelist = []
	# Start
	sshdeviceip = sshdevice.get('Device IPs').encode('utf-8')
	sshdevicevendor = sshdevice.get('Vendor').encode('utf-8')
	sshdevicetype = sshdevice.get('Type').encode('utf-8')
	sshdevicetype = sshdevicevendor.lower() + "_" + sshdevicetype.lower()
	# Device Type Assignment
	deviceswitch = 0
	devicerouter = 0
	deviceasa = 0
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
		except NameError:
			print 'Error with connecting to the device ' + sshdeviceip + '. Login was unsuccessful. Please validate out of band.'
			sys.exit()
		except Exception as e:
			print 'Error with connecting to the device ' + sshdeviceip + '. Error is ' + str(e)
			sys.exit()
		sshdevicehostname = sshnet_connect.find_prompt()
		sshdevicehostname = sshdevicehostname.strip('#')
		if '>' in sshdevicehostname:
			sshnet_connect.enable()
			sshdevicehostname = sshdevicehostname.strip('>')
			sshdevicehostname = sshnet_connect.find_prompt()
			sshdevicehostname = sshdevicehostname.strip('#')
		print 'Successfully connected to ' + sshdevicehostname + ' (' + sshdeviceip + ')'
		print 'Gathering data from ' + sshdevicehostname
		#Create output folder if none exists
		outputfolder = exportlocation + '\\' + sshdevicehostname
		if not os.path.exists(outputfolder):
			os.makedirs(outputfolder)
		#################################################################
		################### DOWNLOAD TEMPLATES START ####################
		#################################################################
		# Show Inventory
		if "cisco_ios" in sshdevicetype.lower():
			templatename = "cisco_ios_show_inventory.template"
		if "cisco_xe" in sshdevicetype.lower():
			templatename = "cisco_ios_show_inventory.template"
		if "cisco_nxos" in sshdevicetype.lower():
			templatename = "cisco_nxos_show_inventory.template"
		# Create template file path
		templatefile = os.path.join(templatepath,templatename)
		# Open and store in memory
		with open(templatefile, 'r') as fsmtemplatenamefile:
			fsminvtemplate = textfsm.TextFSM(fsmtemplatenamefile)
		# IP Arp Table
		if "cisco_ios" in sshdevicetype.lower():
			templatename = "cisco_ios_show_iparp.template"
		if "cisco_xe" in sshdevicetype.lower():
			templatename = "cisco_ios_show_iparp.template"
		if "cisco_nxos" in sshdevicetype.lower():
			templatename = "cisco_nxos_show_iparp.template"
		# Create template file path
		templatefile = os.path.join(templatepath,templatename)
		# Open and store in memory
		with open(templatefile, 'r') as fsmtemplatenamefile:
			fsmarptemplate = textfsm.TextFSM(fsmtemplatenamefile)
		# Mac Table Lists
		if "cisco_ios" in sshdevicetype.lower():
			templatename = "cisco_ios_show_mac.template"
		if "cisco_xe" in sshdevicetype.lower():
			templatename = "cisco_ios_show_mac.template"
		if "cisco_nxos" in sshdevicetype.lower():
			templatename = "cisco_nxos_show_mac.template"
		# Create template file path
		templatefile = os.path.join(templatepath,templatename)
		# Open and store in memory
		with open(templatefile, 'r') as fsmtemplatenamefile:
			fsmmactemplate = textfsm.TextFSM(fsmtemplatenamefile)
		# Show License
		if "cisco_ios" in sshdevicetype.lower():
			templatename = "cisco_ios_show_license.template"
		if "cisco_xe" in sshdevicetype.lower():
			templatename = "cisco_ios_show_license.template"
		if "cisco_nxos" in sshdevicetype.lower():
			templatename = "cisco_nxos_show_license.template"
		# Create template file path
		templatefile = os.path.join(templatepath,templatename)
		# Open and store in memory
		with open(templatefile, 'r') as fsmtemplatenamefile:
			fsmlictemplate = textfsm.TextFSM(fsmtemplatenamefile)
		# Show Version/License
		if "cisco_ios" in sshdevicetype.lower():
			templatename = "cisco_ios_show_version_lic.template"
		if "cisco_xe" in sshdevicetype.lower():
			templatename = "cisco_ios_show_version_lic.template"
		if "cisco_nxos" in sshdevicetype.lower():
			templatename = "cisco_nxos_show_license.template"
		# Create template file path
		templatefile = os.path.join(templatepath,templatename)
		# Open and store in memory
		with open(templatefile, 'r') as fsmtemplatenamefile:
			fsmverlictemplate = textfsm.TextFSM(fsmtemplatenamefile)
		# Show Version
		if "cisco_ios" in sshdevicetype.lower():
			templatename = "cisco_ios_show_version.template"
		if "cisco_xe" in sshdevicetype.lower():
			templatename = "cisco_ios_show_version.template"
		if "cisco_nxos" in sshdevicetype.lower():
			templatename = "cisco_nxos_show_version.template"
		# Create template file path
		templatefile = os.path.join(templatepath,templatename)
		# Open and store in memory
		with open(templatefile, 'r') as fsmtemplatenamefile:
			fsmvertemplate = textfsm.TextFSM(fsmtemplatenamefile)
		# Show Interface Status
		if "cisco_ios" in sshdevicetype.lower():
			templatename = "cisco_ios_show_interface_stat.template"
		if "cisco_xe" in sshdevicetype.lower():
			templatename = "cisco_ios_show_interface_stat.template"
		if "cisco_nxos" in sshdevicetype.lower():
			templatename = "cisco_nxos_show_interface_stat.template"
		# Create template file path
		templatefile = os.path.join(templatepath,templatename)
		# Open and store in memory
		with open(templatefile, 'r') as fsmtemplatenamefile:
			fsmintstattemplate = textfsm.TextFSM(fsmtemplatenamefile)
		# Show Power Inline
		if "cisco_ios" in sshdevicetype.lower():
			templatename = "cisco_ios_show_powerinline.template"
		if "cisco_xe" in sshdevicetype.lower():
			templatename = "cisco_ios_show_powerinline.template"
		if 'cisco_nxos' in sshdevicetype.lower():
			templatename = "cisco_nxos_show_enviroment_power.template"
		# Create template file path
		templatefile = os.path.join(templatepath,templatename)
		# Open and store in memory
		with open(templatefile, 'r') as fsmtemplatenamefile:
			fsmpoeporttemplate = textfsm.TextFSM(fsmtemplatenamefile)
		# Show IP Interface Brief
		if "cisco_ios" in sshdevicetype.lower():
			templatename = "cisco_ios_show_ipintbr.template"
		if "cisco_xe" in sshdevicetype.lower():
			templatename = "cisco_ios_show_ipintbr.template"
		if "cisco_nxos" in sshdevicetype.lower():
			templatename = "cisco_nxos_show_ipintbr.template"
		# Create template file path
		templatefile = os.path.join(templatepath,templatename)
		# Open and store in memory
		with open(templatefile, 'r') as fsmtemplatenamefile:
			fsmipintbrtemplate = textfsm.TextFSM(fsmtemplatenamefile)
		# Show Interface Transceiver
		if "cisco_nxos" in sshdevicetype.lower():
			templatename = "cisco_nxos_show_inttrans.template"
			# Create template file path
			templatefile = os.path.join(templatepath,templatename)
			# Open and store in memory
			with open(templatefile, 'r') as fsmtemplatenamefile:
				fsminttranstemplate = textfsm.TextFSM(fsmtemplatenamefile)
		#################################################################
		##################### DOWNLOAD TEMPLATES END ####################
		#################################################################
		#
		#
		#
		#
		#
		#################################################################
		###################### STANDARD ALL START #######################
		#################################################################
		######################## Show Running Config #########################
		sshcommand = showrun
		sshresult = sshnet_connect.send_command(sshcommand)
		showrunresult = sshresult
		writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
		######################## Show Startup Config #########################
		sshcommand = showstart
		sshresult = sshnet_connect.send_command(sshcommand)
		writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
		######################## Show CDP Neighbors #########################
		sshcommand = showcdp
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
		######################## Show LLDP Neighbors #########################
		sshcommand = showlldp
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		######################## Show License #########################
		if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
			sshcommand = showver
		if 'cisco_nxos' in sshdevicetype.lower():
			sshcommand = showlic
		sshresult = sshnet_connect.send_command(sshcommand)
		# Create temporary license information DB
		templicenseinfo = []
		imagepath = ''
		foundlicense = 0
		if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
			data = fsmverlictemplate.ParseText(sshresult)
			for subrow in data:
				if subrow[0] != '':
					templicenseinfo.append(subrow[0])
					foundlicense = 1
				if subrow[2] != '':
					imagepath = subrow[2]
			if foundlicense == 0:
				# Classic switch licenses
				if 'lanlite' in imagepath.lower():
					templicenseinfo.append('lanlite')
					foundlicense = 1
				if 'lanbase' in imagepath.lower():
					templicenseinfo.append('lanbase')
					foundlicense = 1
				if 'ipbase' in imagepath.lower():
					templicenseinfo.append('ipbase')
					foundlicense = 1
				if 'ipservices' in imagepath.lower():
					templicenseinfo.append('ipservices')
					foundlicense = 1
				# Classic router licenses
				if 'ipvoice' in imagepath.lower():
					templicenseinfo.append('ipvoice')
					foundlicense = 1
				if 'advipservices' in imagepath.lower():
					templicenseinfo.append('advipservices')
					foundlicense = 1
				if 'spservices' in imagepath.lower():
					templicenseinfo.append('spservices')
					foundlicense = 1
				if 'advsecurity' in imagepath.lower():
					templicenseinfo.append('advsecurity')
					foundlicense = 1
				if 'entservices' in imagepath.lower():
					templicenseinfo.append('entservices')
					foundlicense = 1
				if 'entbase' in imagepath.lower():
					templicenseinfo.append('entbase')
					foundlicense = 1
				if 'entservices' in imagepath.lower():
					templicenseinfo.append('entservices')
					foundlicense = 1
				if 'adventerprise' in imagepath.lower():
					templicenseinfo.append('adventerprise')
					foundlicense = 1
			if foundlicense == 0:
				# New licensing, only visible via show license
				sshcommand = showlic
				sshresult = sshnet_connect.send_command(sshcommand)
				data = fsmlictemplate.ParseText(sshresult)
				for subrow in data:
					if subrow[0] != '':
						templicenseinfo.append(subrow[0])
		if 'cisco_nxos' in sshdevicetype.lower():
			data = fsmlictemplate.ParseText(sshresult)
			for subrow in data:
				if subrow[0] != '':
					templicenseinfo.append(subrow[0])
		######################## Show Version #########################
		sshcommand = showver
		sshresult = sshnet_connect.send_command(sshcommand)
		#### Find Type of Device ####
		if any(word in sshresult for word in switchlist):
			deviceswitch = 1
		if any(word in sshresult for word in routerlist):
			devicerouter = 1
		if any(word in sshresult for word in fwlist):
			devicefw = 1
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
		# Export Version, used later in the full inventory list (NOT A GLOBAL LIST) #
		data = fsmvertemplate.ParseText(sshresult)
		tempversioninfo = []
		if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
			for subrow in data:
				# Get Version Number and attach to temporary dictionary
				ver_ver = subrow[0]
				ver_host = subrow[2]
				# Create Temp Dictionary
				tempdict = {}
				# Append Data to Temp Dictionary
				tempdict['Version'] = ver_ver
				tempdict['Hostname'] = ver_host
				# Append Temp Dictionary to Global List
				tempversioninfo.append(tempdict)
		if 'cisco_nxos' in sshdevicetype.lower():
			for subrow in data:
				# Get Version Number and attach to temporary dictionary
				ver_ver = subrow[2]
				ver_host = sshdevicehostname
				# Create Temp Dictionary
				tempdict = {}
				# Append Data to Temp Dictionary
				tempdict['Version'] = ver_ver
				tempdict['Hostname'] = ver_host
				# Append Temp Dictionary to Global List
				tempversioninfo.append(tempdict)
		######################## Show Location #########################
		if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
			sshcommand = showlocation
			sshresult = sshnet_connect.send_command(sshcommand)
			inv_location = removeprefix(sshresult,'snmp-server location ')
		if 'cisco_nxos' in sshdevicetype.lower():
			sshcommand = showlocation_nxos
			sshresult = sshnet_connect.send_command(sshcommand)
			inv_location = removeprefix(sshresult,'snmp-server location ')
		######################## Show Inventory #########################
		sshcommand = showinv
		sshresult = sshnet_connect.send_command(sshcommand)
		# Find Type of Device #
		if any(word in sshresult for word in switchlist):
			deviceswitch = 1
		if any(word in sshresult for word in routerlist):
			devicerouter = 1
		if any(word in sshresult for word in fwlist):
			devicefw = 1
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
		# Export Inventory #
		data = fsminvtemplate.ParseText(sshresult)
		if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
			for subrow in data:
				# Get Product Name, Product Serial Number, Description and Stack
				inv_pid = subrow[2]
				inv_sn = subrow[4]
				inv_name = subrow[0]
				if re.match('^[1-8]$',subrow[0]) or re.match('^Switch [1-8]$',subrow[0]):
					if re.match('^Switch [1-8]$',subrow[0]):
						try:
							inv_stack = re.search('^Switch ([1-8])$',subrow[0]).group(1)
						except:
							inv_stack = subrow[0]
						inv_desc = 'Switch chassis'
					else:
						inv_stack = subrow[0]
						inv_desc = 'Switch chassis'
				else:
					inv_stack = ''
					inv_desc = subrow[0]
				if re.match('^GLC|SFP.*',inv_pid):
					inv_desc = subrow[1]
				# Get Version number from already created list
				inv_ver = ''
				for subrow1 in tempversioninfo:
					if sshdevicehostname == subrow1.get('Hostname'):
						inv_ver = subrow1.get('Version')
						break
				# Get License number from already created list
				inv_license = ','.join(templicenseinfo)
				# Create Temp Dictionary
				tempdict = {}
				# Append Data to Temp Dictionary
				tempdict['Hostname'] = sshdevicehostname
				tempdict['Product ID'] = inv_pid
				tempdict['Serial Number'] = inv_sn
				tempdict['Description'] = inv_desc
				tempdict['Stack Number'] = inv_stack
				tempdict['Version'] = inv_ver
				tempdict['License'] = inv_license
				tempdict['Location'] = inv_location
				tempdict['Name'] = inv_name
				# Append Temp Dictionary to Global List
				fullinventorylist.append(tempdict)
		if 'cisco_nxos' in sshdevicetype.lower():
			for subrow in data:
				# Get Product Name, Product Serial Number, Description and Stack
				inv_pid = subrow[2]
				inv_sn = subrow[4]
				inv_desc = subrow[1]
				inv_name = subrow[0]
				inv_ver = ''
				# Get Version number from already created list
				for subrow1 in tempversioninfo:
					if sshdevicehostname == subrow1.get('Hostname'):
						inv_ver = subrow1.get('Version')
						break
				# Get Version number from already created list
				inv_license = ','.join(templicenseinfo)
				# Create Temp Dictionary
				tempdict = {}
				# Append Data to Temp Dictionary
				tempdict['Hostname'] = sshdevicehostname
				tempdict['Product ID'] = inv_pid
				tempdict['Serial Number'] = inv_sn
				tempdict['Description'] = inv_desc
				tempdict['Stack Number'] = ''
				tempdict['Version'] = inv_ver
				tempdict['License'] = inv_license
				tempdict['Location'] = inv_location
				tempdict['Name'] = inv_name
				# Append Temp Dictionary to Global List
				fullinventorylist.append(tempdict)
			# Get transciever info
			sshcommand = showinttrans
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
			# Export Transceiver #
			data = fsminttranstemplate.ParseText(sshresult)
			for subrow in data:
				# Get Product Name, Product Serial Number, Description and Stack
				inv_pid = subrow[2]
				inv_sn = subrow[3]
				inv_desc = subrow[1]
				inv_name = subrow[0]
				inv_ver = ''
				# Get Version number from already created list
				for subrow1 in tempversioninfo:
					if sshdevicehostname == subrow1.get('Hostname'):
						inv_ver = subrow1.get('Version')
						break
				# Create Temp Dictionary
				tempdict = {}
				# Append Data to Temp Dictionary
				tempdict['Hostname'] = sshdevicehostname
				tempdict['Product ID'] = inv_pid
				tempdict['Serial Number'] = inv_sn
				tempdict['Description'] = inv_desc
				tempdict['Stack Number'] = ''
				tempdict['Version'] = inv_ver
				tempdict['Location'] = inv_location
				tempdict['Name'] = inv_name
				# Append Temp Dictionary to Global List
				fullinventorylist.append(tempdict)
		#################################################################
		######################## STANDARD ALL END #######################
		#################################################################
		#
		#
		#
		#
		#
		#################################################################
		##################### SWITCH SPECIFIC START #####################
		#################################################################
		if deviceswitch == 1:
			######################## Show Mac Address #########################
			sshcommand = showmacaddress
			sshresult = sshnet_connect.send_command(sshcommand)
			if 'invalid' in sshresult:
				sshcommand = showmacaddress_older
				sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
			# Export Mac Address Table
			data = fsmmactemplate.ParseText(sshresult)
			# Get MAC Interface Count
			macintcountb = []
			macintcount = []
			if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
				for macintrow0 in data:
					macintname = macintrow0[3]
					tempdict = {}
					# Duplicate Detection
					dupdetect = 0
					for subrow2 in macintcountb:
						if subrow2.get('Interface') == macintname:
							dupdetect = 1
							break
					if dupdetect == 0:
						tempdict['Interface'] = macintname
						macintcountb.append(tempdict)
				for macintrow1 in macintcountb:
					maccount = 0
					macint = macintrow1.get('Interface')
					for subrow2 in data:
						if subrow2[3] == macintrow1.get('Interface'):
							maccount = maccount + 1
					tempdict = {}
					tempdict['Count'] = maccount
					tempdict['Interface'] = macint
					macintcount.append(tempdict)
				# Get MAC addresses and append mac count
				for macintrow2 in data:	
					# Get Hostname, MAC, VLAN, Interface, Count
					mac_host = sshdevicehostname
					mac_mac = macintrow2[0]
					mac_vlan = macintrow2[2]
					mac_int = macintrow2[3]
					for subrow2 in macintcount:
						if mac_int == subrow2.get('Interface'):
							mac_count = subrow2.get('Count')
					# Create Temp Dictionary
					tempdict = {}
					# Append Data to Temp Dictionary
					tempdict['Hostname'] = mac_host
					tempdict['MAC'] = mac_mac
					tempdict['VLAN'] = mac_vlan
					tempdict['Interface'] = mac_int
					tempdict['Count'] = mac_count
					mactablelist.append(tempdict)
			if 'cisco_nxos' in sshdevicetype.lower():
				for macintrow0 in data:
					macintname = macintrow0[6]
					tempdict = {}
					# Duplicate Detection
					dupdetect = 0
					for subrow2 in macintcountb:
						if subrow2.get('Interface') == macintname:
							dupdetect = 1
							break
					if dupdetect == 0:
						tempdict['Interface'] = macintname
						macintcountb.append(tempdict)
				for macintrow1 in macintcountb:
					maccount = 0
					macint = macintrow1.get('Interface')
					for subrow2 in data:
						if subrow2[6] == macintrow1.get('Interface'):
							maccount = maccount + 1
					tempdict = {}
					tempdict['Count'] = maccount
					tempdict['Interface'] = macint
					macintcount.append(tempdict)
				# Get MAC addresses and append mac count
				for macintrow2 in data:	
					# Get Hostname, MAC, VLAN, Interface, Count
					mac_host = sshdevicehostname
					mac_mac = macintrow2[1]
					mac_vlan = macintrow2[0]
					mac_int = macintrow2[6]
					for subrow2 in macintcount:
						if mac_int == subrow2.get('Interface'):
							mac_count = subrow2.get('Count')
					# Create Temp Dictionary
					tempdict = {}
					# Append Data to Temp Dictionary
					tempdict['Hostname'] = mac_host
					tempdict['MAC'] = mac_mac
					tempdict['VLAN'] = mac_vlan
					tempdict['Interface'] = mac_int
					tempdict['Count'] = mac_count
					mactablelist.append(tempdict)
			######################## Show Power Budget #########################
			######################## Show Power Inline #########################
			if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
				sshcommand = showpowerinline
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
				# Export Power Inline
				data = fsmpoeporttemplate.ParseText(sshresult)
				for subrow in data:
					# Get Int, Admin, Oper, Power, Device, Class, Max POE
					pow_oper = subrow[2]
					if 'on' in pow_oper.lower():
						pow_oper = 'Up'
					else:
						pow_oper = 'Down'
					# Create Temp Dictionary
					tempdict = {}
					# Append Data to Temp Dictionary
					tempdict['Hostname'] = sshdevicehostname
					tempdict['Interface'] = subrow[0]
					tempdict['Admin Status'] = subrow[1]
					tempdict['Up/Down'] = pow_oper
					tempdict['Power Usage'] = subrow[3]
					tempdict['Device Name'] = subrow[4]
					tempdict['Device Class'] = subrow[5]
					tempdict['Max POE Capability'] = subrow[6]
					# Append Temp Dictionary to Global List
					poeinterfacelist.append(tempdict)
				######################## Show Stack Power #########################
				sshcommand = showstackpower
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
						writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
			if 'cisco_nxos' in sshdevicetype.lower():
				sshcommand = showpowerinline_nxos
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
			#Show Switch Stack
			sshcommand = showswitch
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)			
			#Show DHCP Snooping
			sshcommand = showdhcpsnooping
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
			#Show VLAN
			sshcommand = showvlan
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)		
			#Show Trunk
			sshcommand = showtrunk
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			#Show Spanning-Tree
			sshcommand = showspanning
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			#Show Spanning-Tree Blocked
			sshcommand = showspanningblock
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
		#################################################################
		##################### SWITCH SPECIFIC END #######################
		#################################################################
		#
		#
		#
		#
		#
		#################################################################
		#################### ROUTING SPECIFIC START #####################
		#################################################################
		if 'route' in showrunresult.lower() or 'cisco_nxos' in sshdevicetype:
			######################## Show IP ARP #########################
			sshcommand = showiparp
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
			# Export ARP Data
			data = fsmarptemplate.ParseText(sshresult)
			for subrow in data:
				# Get IP, MAC, and Interface
				arp_ip = subrow[0]
				# Dup Detect
				dupdetect = 0
				for duprow in ipmactablelist:
					duprowip = duprow.get('IP Address')
					if duprowip == arp_ip:
						dupdetect = 1
						break
				# If no duplicate, append to dictionary/list
				if dupdetect == 1:
					pass
				else:
					arp_age = subrow[1]
					arp_mac = subrow[2]
					arp_host = sshdevicehostname
					arp_int = subrow[3]
					# Create Temp Dictionary
					tempdict = {}
					# Append Data to Temp Dictionary
					tempdict['IP Address'] = arp_ip
					tempdict['MAC'] = arp_mac
					tempdict['Age'] = arp_age
					tempdict['Hostname'] = arp_host
					tempdict['Interface'] = arp_int
					# Append Temp Dictionary to Global List
					ipmactablelist.append(tempdict)
			######################## Show Route Table #########################
			sshcommand = showiproute
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			if 'router eigrp' in showrunresult.lower():
				#Show EIGRP Neighbors
				sshcommand = showeigrpnei
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
				#Show EIGRP Topology
				sshcommand = showeigrptop
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			if 'router ospf' in showrunresult.lower():
				#Show OSPF Neighbors
				sshcommand = showospfnei
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
				#Show OSPF Database
				sshcommand = showospfdata
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			if 'router bgp' in showrunresult.lower():
				#Show BGP Neighbors
				sshcommand = showbgpnei
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
				#Show BGP Table
				sshcommand = showbgptable
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		if 'multicast-routing' in showrunresult.lower():
			#Show PIM Neighbors
			sshcommand = showippimnei
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			#Show MRoutes
			sshcommand = showmroute
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		#################################################################
		#################### ROUTING SPECIFIC END #######################
		#################################################################
		#
		#
		#
		#
		#
		#################################################################
		########################## MISC START ###########################
		#################################################################
		#
		######################## Show Interface Statistics #########################
		sshcommand = showinterfacestat
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
		# Export Interface Statistics #
		data = fsmintstattemplate.ParseText(sshresult)
		for subrow in data:
			# Get Interface,Description,Status,VLAN,Duplex,Speed,Type
			# Create Temp Dictionary
			tempdict = {}
			# Append Data to Temp Dictionary
			tempdict['Hostname'] = sshdevicehostname
			tempdict['Interface'] = subrow[0]
			tempdict['Description'] = subrow[1]
			tempdict['Status'] = subrow[2]
			tempdict['VLAN'] = subrow[3]
			tempdict['Duplex'] = subrow[4]
			tempdict['Speed'] = subrow[5]
			tempdict['Type'] = subrow[6]
			# Append Temp Dictionary to Global List
			l2interfacelist.append(tempdict)
		######################## Show IP Interface Brief #########################
		sshcommand = showipintbr
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
		data = fsmipintbrtemplate.ParseText(sshresult)
		if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
			for subrow in data:
				# Get Interface,Description,Status,VLAN,Duplex,Speed,Type
				# Create Temp Dictionary
				tempdict = {}
				# Append Data to Temp Dictionary
				tempdict['Hostname'] = sshdevicehostname
				tempdict['Interface'] = subrow[0]
				tempdict['IP Address'] = subrow[1]
				tempdict['Status'] = subrow[2]
				tempdict['Line Protocol'] = subrow[3]
				# Append Temp Dictionary to Global List
				l3interfacelist.append(tempdict)
		if 'cisco_nxos' in sshdevicetype.lower():
			for subrow in data:
				# Get Interface,Description,Status,VLAN,Duplex,Speed,Type
				# Create Temp Dictionary
				tempdict = {}
				# Modify Values
				
				# Append Data to Temp Dictionary
				tempdict['Hostname'] = sshdevicehostname
				tempdict['VRF'] = subrow[0]
				tempdict['Interface'] = subrow[1]
				tempdict['IP Address'] = subrow[2]
				tempdict['Status'] = subrow[5]
				tempdict['Line Protocol'] = subrow[3]
				# Append Temp Dictionary to Global List
				l3interfacelist.append(tempdict)
		######################## Show IGMP Snooping #########################
		sshcommand = showigmpsnoop
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		#Show IGMP Membership
		sshcommand = showipigmpmember
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		#Show VRF
		sshcommand = showvrf
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		#Show Temperature
		if 'cisco_ios' in sshdevicetype.lower() or 'cisco_xe' in sshdevicetype.lower():
			sshcommand = showtemp
			sshresult = sshnet_connect.send_command(sshcommand)
		if 'cisco_nxos' in sshdevicetype.lower():
			sshcommand = showtemp_nxos
			sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			writeoutput (sshcommand,sshresult,sshdevicehostname,outputfolder)
		# End
		print 'Completed device information gathering for ' + sshdevicehostname
		#################################################################
		########################### MISC END ############################
		#################################################################
		sshnet_connect.disconnect()
	except IndexError:
		print 'Could not connect to device ' + sshdeviceip
		try:
			sshnet_connect.disconnect()
		except:
			pass
	except Exception as e:
		print 'Error while gathering data on ' + sshdeviceip + '. Error is ' + str(e)
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
	for file in tempfilelist:
		try:
			os.remove(file)
		except:
			pass
	return fullinventorylist,ipmactablelist,mactablelist,iparptablelist,l2interfacelist,l3interfacelist,poeinterfacelist