#!/usr/bin/env python
'''
---AUTHOR---
Name: Matt Cross
Email: routeallthings@gmail.com

---PREREQ---
INSTALL netmiko (pip install netmiko)
INSTALL textfsm (pip install textfsm)
INSTALL openpyxl (pip install openpyxl)
INSTALL fileinput (pip install fileinput)
INSTALL xlhelper (python -m pip install git+git://github.com/routeallthings/xlhelper.git)
'''
'''Module Imports (Native)'''
import re
import getpass
import os
import unicodedata
import csv
import threading
import time
import sys

'''Module Imports (Non-Native)'''
try:
	import netmiko
	from netmiko import ConnectHandler
except ImportError:
	netmikoinstallstatus = fullpath = raw_input ('Netmiko module is missing, would you like to automatically install? (Y/N): ')
	if "Y" in netmikoinstallstatus.upper() or "YES" in netmikoinstallstatus.upper():
		os.system('python -m pip install netmiko')
		import netmiko
		from netmiko import ConnectHandler
	else:
		print "You selected an option other than yes. Please be aware that this script requires the use of netmiko. Please install manually and retry"
		sys.exit()
try:
	import textfsm
except ImportError:
	textfsminstallstatus = fullpath = raw_input ('textfsm module is missing, would you like to automatically install? (Y/N): ')
	if "Y" in textfsminstallstatus.upper() or "YES" in textfsminstallstatus.upper():
		os.system('python -m pip install textfsm')
		import textfsm
	else:
		print "You selected an option other than yes. Please be aware that this script requires the use of textfsm. Please install manually and retry"
		sys.exit()
try:
	from openpyxl import load_workbook
except ImportError:
	requestsinstallstatus = fullpath = raw_input ('openpyxl module is missing, would you like to automatically install? (Y/N): ')
	if 'Y' in requestsinstallstatus or 'y' in requestsinstallstatus or 'yes' in requestsinstallstatus or 'Yes' in requestsinstallstatus or 'YES' in requestsinstallstatus:
		os.system('python -m pip install openpyxl')
		from openpyxl import load_workbook
	else:
		print 'You selected an option other than yes. Please be aware that this script requires the use of Pandas. Please install manually and retry'
		sys.exit()
#
try:
	import fileinput
except ImportError:
	requestsinstallstatus = fullpath = raw_input ('FileInput module is missing, would you like to automatically install? (Y/N): ')
	if 'Y' in requestsinstallstatus or 'y' in requestsinstallstatus or 'yes' in requestsinstallstatus or 'Yes' in requestsinstallstatus or 'YES' in requestsinstallstatus:
		os.system('python -m pip install FileInput')
		import FileInput
	else:
		print 'You selected an option other than yes. Please be aware that this script requires the use of FileInput. Please install manually and retry'
		sys.exit()
#	
# Darth-Veitcher Module https://github.com/darth-veitcher/xlhelper
#
from pprint import pprint
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string
from collections import OrderedDict
try:
	import xlhelper
except ImportError:
	requestsinstallstatus = fullpath = raw_input ('xlhelper module is missing, would you like to automatically install? (Y/N): ')
	if 'Y' in requestsinstallstatus or 'y' in requestsinstallstatus or 'yes' in requestsinstallstatus or 'Yes' in requestsinstallstatus or 'YES' in requestsinstallstatus:
		os.system('python -m pip install git+git://github.com/routeallthings/xlhelper.git')
		import xlhelper
	else:
		print 'You selected an option other than yes. Please be aware that this script requires the use of xlhelper. Please install manually and retry'
		sys.exit()

'''Global Variables'''
ipv4_address = re.compile('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')

#Creation of SSH commands
showrun = "show running-config"
showstart = "show startup-config"
showver = "show version"
showinv = "show inventory"
showcdp = "show cdp neighbors detail"
showlldp = "show lldp neighbors detail"
showpowerinline = "show power inline"
showstackpower = "show stack-power detail"
showswitch = "show switch detail"
showdhcpsnooping = "show ip dhcp snooping"
showvlan = "show vlan"
showtrunk = "show interface trunk"
showspanning = "show spanning-tree"
showspanningblock = "show spanning-tree blockedports"
showinterfacestat = "show interface status"
showipintbr = "show ip interface brief"
showeigrpnei = "show ip eigrp neighbors"
showeigrptop = "show ip eigrp topology all"
showospfnei = "show ip ospf neighbors"
showospfdata = "show ip ospf database"
showbgpnei = "show ip bgp neighbors"
showbgptable = "show ip bgp"
showiproute = "show ip route"
showvrf = "show vrf"
showtemp = "show env temperature status"
showippimnei = "show ip pim neighbor"
showmroute = "show ip mroute"
showigmpsnoop = "show ip igmp snooping"
showipigmpmember = "show ip igmp membership"
showinterface = "show interface"


'''Global Variable Questions'''
print ''
print 'Device Validator'
print '##########################################################'
print 'The purpose of this tool is to use a XLSX import to check'
print 'and compare information in the file against the device.'
print 'Please fill in the configuration tab on the templated'
print 'XLSX sheet, along with all the data that you want to test.'
print '##########################################################'
print ''
print '----Questions that need answering----'
excelfilelocation = raw_input('File to load the excel data from (e.g. C:/Python27/dv-variables.xlsx):')
if excelfilelocation == '':
	excelfilelocation = 'C:/Python27/dv-variables.xlsx'
excelfilelocation = excelfilelocation.replace('"', '')
# Load Configuration Variables
configdict = {}
for configvariables in xlhelper.sheet_to_dict(excelfilelocation,'Config'):
	try:
		configvar = configvariables.get('Variable').encode('utf-8')
		configval = configvariables.get('Value').encode('utf-8')
	except:
		configvar = configvariables.get('Variable')
		configval = configvariables.get('Value')
	configdict[configvar] = configval
# Username Variables/Questions
sshusername = configdict.get('Username')
if 'NA' == sshusername:
	sshusername = raw_input('What is the username you will use to login to the equipment?:')
sshpassword = configdict.get('Password')
if 'NA' == sshpassword:
	sshpassword = getpass.getpass('What is the password you will use to login to the equipment?:')
enablesecret = configdict.get('EnableSecret')
if 'NA' == enablesecret:
	enablesecret = getpass.getpass('What is the enable password you will use to access the device?:')
# Rest of the Config Variables
exportlocation = configdict.get('ExportLocation')
if exportlocation == '':
	exportlocation = r'C:\OutputFolder'
configurationv = configdict.get('Configuration')
if configurationv == None:
	configurationv = 'True'
healthcheckv = configdict.get('HealthCheck')
if healthcheckv == None:
	healthcheckv = 'True'
internetips = configdict.get('internetips')
if internetips == None:
	internetips = '8.8.8.8,4.2.2.2'
if ',' in internetips:
	internetips = internetips.split(',')
iperftest = configdict.get('iPerfTest')
if iperftest == None:
	iperftest = 'N'
iperftesttype = configdict.get('iPerfTestType')
if iperftesttype == None:
	iperftesttype = 'Bandwidth'
iperftestips = configdict.get('iPerfTestIPs')
if not iperftestips == None:
	if ',' in iperftestips:
		iperftestips = iperftestips.split(',')
routingprotocol = configdict.get('RoutingProtocol')
if routingprotocol == None:
	routingprotocol = 'NA'
failovertest = configdict.get('FailoverTest')
if failovertest == None:
	failovertest = 'N'
failovertestinterfaces = configdict.get('FailoverTestInterfaces')
failoversourceinterfaces = configdict.get('FailoverSourceInterfaces')
powerbudget = configdict.get('PowerBudget')
if powerbudget == None:
	powerbudget = 'Y'
dhcpsnooping = configdict.get('DHCPSnooping')
if dhcpsnooping == None:
	dhcpsnooping = 'Y'
temperature = configdict.get('Temperature')
if temperature == None:
	temperature = 'Y'
# End of Config Variables
# Start of Functions
def DEF_STARTALLTESTS(sshdevice):
	if configurationv == 1:
		DEF_GATHERDATA(sshdevice)
	if healthcheckv == 1:
		#DEF_HEALTHCHECK(sshdevice)
		print ''

def DEF_WRITEOUTPUT(sshcommand,sshresult,sshdevicehostname,outputfolder):
	sshcommandfile = sshcommand.replace(' ','')
	sshcommandfile = sshcommandfile.replace('-','')
	outputfile = outputfolder + '\\' + sshdevicehostname + '_' + sshcommandfile + '.txt'
	f = open(outputfile,'w')
	f.write(sshresult)
	f.close()

##### FUNCTION FOR CONFIGURATION GATHERING #####
def DEF_GATHERDATA(sshdevice):
	sshdeviceip = sshdevice.get('Device IPs').encode('utf-8')
	sshdevicevendor = sshdevice.get('Vendor').encode('utf-8')
	sshdevicetype = sshdevice.get('Type').encode('utf-8')
	sshdevicetype = sshdevicevendor.lower() + "_" + sshdevicetype.lower()
	# Device Type Assignment
	deviceswitch = 'n'
	devicerouter = 'n'
	deviceasa = 'n'
	if 'nxos' in sshdevicetype:
		deviceswitch = 'y'
	#Start Connection
	try:
		sshnet_connect = ConnectHandler(device_type=sshdevicetype, ip=sshdeviceip, username=sshusername, password=sshpassword, secret=enablesecret)
		sshdevicehostname = sshnet_connect.find_prompt()
		sshdevicehostname = sshdevicehostname.strip('#')
		if '>' in sshdevicehostname:
			sshnet_connect.enable()
			sshdevicehostname = sshdevicehostname.strip('>')
			sshdevicehostname = sshnet_connect.find_prompt()
			sshdevicehostname = sshdevicehostname.strip('#')
		print 'Successfully connected to ' + sshdevicehostname
		print 'Gathering data from ' + sshdevicehostname
		#Create output folder if none exists
		outputfolder = exportlocation + '\\' + sshdevicehostname
		if not os.path.exists(outputfolder):
			os.makedirs(outputfolder)
		#Show Running
		sshcommand = showrun
		sshresult = sshnet_connect.send_command(sshcommand)
		showrunresult = sshresult
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)
		#Show Start
		sshcommand = showstart
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)
		#Show CDP Neighbors
		sshcommand = showcdp
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)
		#Show LLDP Neighbors
		sshcommand = showlldp
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)		
		#Show Version
		sshcommand = showver
		sshresult = sshnet_connect.send_command(sshcommand)
		#### Find Type of Device ####
		if 'Catalyst' in sshresult:
			deviceswitch = 'y'
		if 'ASA' in sshresult:
			deviceasa = 'y'
		if 'Router' in sshresult:
			devicerouter = 'y'
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)		
		#Show Inventory
		sshcommand = showinv
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)		
		## FIND SWITCH VAR FROM INV##
		if 'y' in deviceswitch.lower():
			# Power Budget
			if 'y' in powerbudget.lower():
				#Show Power Inline
				sshcommand = showpowerinline
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
						DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)				
				#Show Stack Power
				sshcommand = showpowerinline
				sshresult = sshnet_connect.send_command(showstackpower)
				if not 'invalid' in sshresult:
						DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			#Show Switch Stack
			sshcommand = showswitch
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)			
			#Show DHCP Snooping
			if 'y' in dhcpsnooping.lower():
				sshcommand = showdhcpsnooping
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)
			#Show VLAN
			sshcommand = showvlan
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)		
			#Show Trunk
			sshcommand = showtrunk
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			#Show Spanning-Tree
			sshcommand = showspanning
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			#Show Spanning-Tree Blocked
			sshcommand = showspanningblock
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		#Show Interface Statistics
		sshcommand = showinterfacestat
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)		
		#Show IP Interface Brief
		sshcommand = showipintbr
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)					
		## ROUTING PROTOCOLS ##
		if 'ip routing' in showrunresult.lower():
			#Show Routing Table
			sshcommand = showiproute
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			if 'router eigrp' in showrunresult.lower():
				#Show EIGRP Neighbors
				sshcommand = showeigrpnei
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
				#Show EIGRP Topology
				sshcommand = showeigrptop
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			if 'router ospf' in showrunresult.lower():
				#Show OSPF Neighbors
				sshcommand = showospfnei
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
				#Show OSPF Database
				sshcommand = showospfdata
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			if 'router bgp' in showrunresult.lower():
				#Show BGP Neighbors
				sshcommand = showbgpnei
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
				#Show BGP Table
				sshcommand = showbgptable
				sshresult = sshnet_connect.send_command(sshcommand)
				if not 'invalid' in sshresult:
					DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		if 'multicast-routing' in showrunresult.lower():
			#Show PIM Neighbors
			sshcommand = showippimnei
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
			#Show MRoutes
			sshcommand = showmroute
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		#Show IGMP Snooping
		sshcommand = showigmpsnoop
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		#Show IGMP Membership
		sshcommand = showipigmpmember
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		#Show VRF
		sshcommand = showvrf
		sshresult = sshnet_connect.send_command(sshcommand)
		if not 'invalid' in sshresult:
			DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		#Show Temperature
		if 'y' in temperature.lower():
			sshcommand = showtemp
			sshresult = sshnet_connect.send_command(sshcommand)
			if not 'invalid' in sshresult:
				DEF_WRITEOUTPUT (sshcommand,sshresult,sshdevicehostname,outputfolder)	
		sshnet_connect.disconnect()
	except Exception as e:
		print 'Error while gather data with ' + sshdeviceip + '. Either could not connect or error with pulling information'
		print 'The exact error is..'
		print(e)
		try:
			sshnet_connect.disconnect()
		except:
			'''Nothing'''
	except KeyboardInterrupt:
		print 'CTRL-C pressed, exiting script'
		try:
			sshnet_connect.disconnect()
		except:
			'''Nothing'''
	print 'Completed device information gathering for ' + sshdeviceip

def DEF_HEALTHCHECK(sshdevice):
	sshdeviceip = sshdevice.get('Device IPs').encode('utf-8')
	sshdevicevendor = sshdevice.get('Vendor').encode('utf-8')
	sshdevicetype = sshdevice.get('Type').encode('utf-8')
	sshdevicetype = sshdevicevendor.lower() + "_" + sshdevicetype.lower()
	### FSM Templates ###
	# FSM Show Interface
	if "cisco_ios" in sshdevicetype:
		fsmshowinturl = "https://raw.githubusercontent.com/routeallthings/Device-Validator/templates/master/cisco_ios_show_interfaces_health.template"
	if "cisco_xe" in sshdevicetype:
		fsmshowinturl = "https://raw.githubusercontent.com/routeallthings/Device-Validator/templates/master/cisco_ios_show_interfaces_health.template"
	if "cisco_nxos" in sshdevicetype:
		fsmshowinturl = "placeholder"
	fsmtemplatename = sshdevicetype + '_fsmshowint.fsm'
	if not fsmtemplatename.exists():
		urllib.urlretrieve(fsmshowinturl, fsmtemplatename)
	fsmtemplatenamefile = open(fsmtemplatename)
	fsminttemplate = textfsm.TextFSM(fsmtemplatenamefile)
	# FSM Show Temperature
	if "cisco_ios" in sshdevicetype:
		fsmshowinturl = "https://raw.githubusercontent.com/routeallthings/Device-Validator/templates/master/cisco_ios_show_temp_health.template"
	if "cisco_xe" in sshdevicetype:
		fsmshowinturl = "https://raw.githubusercontent.com/routeallthings/Device-Validator/templates/master/cisco_ios_show_temp_health.template"
	if "cisco_nxos" in sshdevicetype:
		fsmshowinturl = "placeholder"	
	fsmtemplatename = sshdevicetype + '_fsmshowtemp.fsm'
	if not fsmtemplatename.exists():
		urllib.urlretrieve(fsmshowinturl, fsmtemplatename)
	fsmtemplatenamefile = open(fsmtemplatename)
	fsmtemptemplate = textfsm.TextFSM(fsmtemplatenamefile)	
	#Start Connection
	try:
		sshnet_connect = ConnectHandler(device_type=sshdevicetype, ip=sshdeviceip, username=sshusername, password=sshpassword, secret=enablesecret)
		sshdevicehostname = sshnet_connect.find_prompt()
		sshdevicehostname = sshdevicehostname.strip('#')
		if '>' in sshdevicehostname:
			sshnet_connect.enable()
			sshdevicehostname = sshdevicehostname.strip('>')
			sshdevicehostname = sshnet_connect.find_prompt()
			sshdevicehostname = sshdevicehostname.strip('#')
		print 'Successfully connected to ' + sshdevicehostname
		print 'Health Check starting on ' + sshdevicehostname
		#Show Interfaces
		sshcommand = showinterface
		sshresult = sshnet_connect.send_command(sshcommand)
		hcshowint = fsminttemplate.ParseText(sshresult)
		#Parse through each interface looking for issues
		for hcshowintsingle in hcshowint:
			hcerrorcount = 0
			hcinterfacename = hcshowintsingle[0].encode('utf-8')
			if not 'notconnect' in hcshowintsingle[2]:
				# Look for duplexing issues
				if 'Half-duplex' in hcshowintsingle[6]:
					hcerror = 'Duplex Mismatch'
					hcdescription = '(Interface is showing as half-duplex. If this is by design please ignore.'
					healthcheckcsv.append (sshdevicehostname,hcerror,hcdescription)
				if '10Mb/s' in hcshowintsingle[7]:
					hcerror = 'Duplex Mismatch'
					hcdescription = 'Interface is showing as 10Mb/s. If this is by design please ignore.'
					healthcheckcsv.append (sshdevicehostname,hcerror,hcdescription)
				# Look for interface counter errors
				# Input Errors
				if hcshowintsingle[8] > 0:
					hcerror = 'Input Errors'
					hcinterfacecounter = hcshowintsingle[8].encode('utf-8')
					hcdescription = 'Interface is showing ' + hcinterfacecounter + ' input errors. Usually indicative of a bad link (cabling and/or optic failure).'
					healthcheckcsv.append (sshdevicehostname,hcerror,hcdescription)
				# CRC errors
				if hcshowintsingle[9] > 0:
					hcerror = 'CRC Errors'
					hcinterfacecounter = hcshowintsingle[9].encode('utf-8')
					hcdescription = 'Interface is showing ' + hcinterfacecounter + ' CRC errors. Usually indicative of incorrect duplexing settings or a bad link (cabling and/or optic failure).'
					healthcheckcsv.append (sshdevicehostname,hcerror,hcdescription)
				# Output errors
				if hcshowintsingle[10] > 10000:
					hcerror = 'Saturated Link'
					hcinterfacecounter = hcshowintsingle[10].encode('utf-8')
					hcdescription = 'Interface is showing ' + hcinterfacecounter + ' output errors. This is usually indicative of a saturated interface.  '
					healthcheckcsv.append (sshdevicehostname,hcerror,hcdescription)
				# Collisions
				if hcshowintsingle[11] > 0:
					hcerror = 'Shared Medium'
					hcinterfacecounter = hcshowintsingle[11].encode('utf-8')
					hcdescription = 'Interface is showing ' + hcinterfacecounter + ' collisions.  '
					healthcheckcsv.append (sshdevicehostname,hcerror,hcdescription)		
				# Interface resets
				if hcshowintsingle[10] > 20:
					hcerror = 'Interface Reset Count'
					hcinterfacecounter = hcshowintsingle[10].encode('utf-8')
					hcdescription = 'Interface is showing ' + hcinterfacecounter + ' interface resets. '
					healthcheckcsv.append (sshdevicehostname,hcerror,hcdescription)
		#Show Temperature
		sshcommand = showtemp
		sshresult = sshnet_connect.send_command(sshcommand)
		hcshowtemp = fsminttemplate.ParseText(sshresult)
		hctempdegrees = hcshowtemp[0].encode('utf-8')
		hctempdegreesint = hctempdegress.int
		if hctempdegreesint > 45:
			hcerror = 'Temperature Alert'
			hcdescription = 'Temperature has been recorded at ' + hctempdegrees + ' Celsius. Please lower the temperature for the surrounding environment '
			healthcheckcsv.append (sshdevicehostname,hcerror,hcdescription)		
	except Exception as e:
		print 'Error while gather data with ' + sshdeviceip + '. Either could not connect or error with pulling information'
		print 'The exact error is..'
		print(e)
		try:
			sshnet_connect.disconnect()
		except:
			'''Nothing'''
	except KeyboardInterrupt:
		print 'CTRL-C pressed, exiting script'
		try:
			sshnet_connect.disconnect()
		except:
			'''Nothing'''
	print 'Completed health check for ' + sshdeviceip		

# Create empty lists
healthcheckcsv = []

# Start of threading
print '----Starting to gather data from equipment----'
if __name__ == "__main__":
	for sshdevice in xlhelper.sheet_to_dict(excelfilelocation,'Device IPs'):
		sshdeviceip = sshdevice.get('Device IPs').encode('utf-8')
		print "Spawning Thread for " + sshdeviceip
		t = threading.Thread(target=DEF_STARTALLTESTS, args=(sshdevice,))
		t.start()
	main_thread = threading.currentThread()
	for it_thread in threading.enumerate():
		if it_thread != main_thread:
			it_thread.join()

# CSV Output for Healthcheck
if healthcheckv == 1:
	savepath = exportlocation + '\\HealthCheck.csv'
	with open(savepath, 'wb') as csvfile:
		fieldnames = ['Hostname', 'Error', 'Description']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		saveresultslistsplit = []
		for saveresultsrow in healthcheckcsv:
			saveresultslistsplit.append(saveresultsrow.strip().split(','))
		saveresultslistsplit = [saveresultslistsplit[i:i+3] for i in range(0,len(saveresultslistsplit),3)]
		for saveresultsplitrow in saveresultslistsplit:
			for saveresultssplitrow2 in saveresultsplitrow:
				saveresultsplitrow1 = saveresultssplitrow2[:1][0]
				saveresultsplitrow2 = saveresultssplitrow2[1:][0]
				saveresultsplitrow3 = saveresultssplitrow2[2:][0]
				writer.writerow({'Hostname': saveresultsplitrow1, 'Error': saveresultsplitrow2, 'Description': saveresultsplitrow3})
		
		