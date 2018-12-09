#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com

# nda.py

# Used for AutoUpdate
import urllib 
import zipfile
import shutil

# Add syspath variable (for executing outside of root folder)
import inspect
import os.path
import sys
filename = inspect.getframeinfo(inspect.currentframe()).filename
rootpath = os.path.dirname(os.path.abspath(filename))
sys.path.append(os.path.join(rootpath,'modules'))
sys.path.append(os.path.join(rootpath,'toolkit'))
# add additional paths, used for auto update component
modulepath = os.path.join(rootpath,'modules')
toolkitpath = os.path.join(rootpath,'toolkit')
macdbpath = os.path.join(rootpath,'macdb')
templatepath = os.path.join(rootpath,'templates')

# Import other required native objects

# Import NDA modules
from ndabase import *
from ndacommands import *
from ndagatherdata import *
from ndahealthcheck import *
from ndacdpdiscovery import *
from ndareports import *

# Start of Toolkit Functions
from addressinnetwork import *
from downloadfile import *
from removeprefix import *
from internetcheck import *
from copytree import *

# Start of NDA Specific Functions


##### GLOBAL VARIABLES + INITIAL MENU #####

# Create empty lists for script use
tempfilelist = []
fullinventorylist = []
ipmactablelist = []
mactablelist = []
iparptablelist = []
l2interfacelist = []
l3interfacelist = []
poeinterfacelist = []
healthchecklist = []
cdpdevicecomplete = []
cdpdevicediscovery = []
sshdevices = []
usernamelist = []
# Start of printable output
print ''
print 'Network Documention Automation'
print '##########################################################'
print 'The purpose of this tool is to pull information from the'
print 'network via CDP/LLDP discovery or manual entry in XLSX.'
print 'Please fill in the configuration tab on the templated'
print 'XLSX sheet, along with all the data that you want to test.'
print '##########################################################'
print ''
# Start of Auto-Update
# Check for Internet
print 'Auto-Update: Testing for Internet'
testserver = "www.google.com"
internettest = internetcheck(testserver)
time.sleep(1)
if internettest == 1:
	autoupdatev = raw_input('Auto-Update: Test Passed, would you like to update (Y/N)?:')
	if 'y' in autoupdatev.lower():
		versioncheckurl = 'https://github.com/routeallthings/Network-Documentation-Automation/raw/master/version.txt'
		versioncheckpath = os.path.join(rootpath,'version.txt')
		with open(versioncheckpath, "r") as currentver:
			currentversion = currentver.read()
		webversion = urllib.urlopen(versioncheckurl).read()
		if currentversion == webversion:
			print 'NDA is already up to date, skipping update'
		else:	
			basezipurl = 'https://github.com/routeallthings/Network-Documentation-Automation/archive/master.zip'
			basezippath = os.path.join(rootpath,'master.zip')
			downloadfile(basezipurl,basezippath)
			with zipfile.ZipFile(basezippath, 'r') as zip_ref:
				for file in zip_ref.namelist():
					if file.startswith('Network-Documentation-Automation-master/'):
						filepath,filename = os.path.split(file)
						finalfilepath = os.path.join(rootpath,filename)
						# Extract folder to \Network-Documentation-Automation-master
						zip_ref.extract(file, rootpath)
						# Print output
						print 'Updating ' + finalfilepath
			# Filepath variable
			filepath = os.path.join(rootpath,'Network-Documentation-Automation-master')			
			# Move contents to root
			copytree(filepath,rootpath)
			# Delete old folder and zip file
			shutil.rmtree(filepath)
			os.remove(basezippath)
			print 'Completed Auto-Update'
			print 'Closing in 5 seconds, please relaunch script'
			time.sleep(5)
			sys.exit()
if internettest == 0:
	print 'Auto-Update: Test Failed, skipping update'
# End of Auto-Update
	
# Getting config excel file
print '----Questions that need answering----'
excelfilelocation = raw_input('File to load the excel data from (e.g. C:/Python27/nda-config.xlsx):')
if excelfilelocation == '':
	excelfilelocation = 'C:/Python27/nda-config.xlsx'
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
for usernames in xlhelper.sheet_to_dict(excelfilelocation,'Username'):
	usernamedict = {}
	try:
		usernamev = usernames.get('Username').encode('utf-8')
		passwordv = usernames.get('Password').encode('utf-8')
		enablev = usernames.get('Enable Password').encode('utf-8')
	except:
		usernamev = usernames.get('Username')
		passwordv = usernames.get('Password')
		enablev = usernames.get('Enable Password')
	try:
		usernamedict['sshusername'] = usernamev
		usernamedict['sshpassword'] = passwordv
		usernamedict['enablesecret'] = enablev
	except:
		pass
	usernamelist.append(usernamedict)
if usernamelist == []:
	sshusername = raw_input('What is the username you will use to login to the equipment?:')
	sshpassword = getpass.getpass('What is the password you will use to login to the equipment?:')
	enablesecret = getpass.getpass('What is the enable password you will use to access the device?:')
# Rest of the Config Variables
exportlocation = configdict.get('ExportLocation')
if exportlocation == '':
	exportlocation = r'C:\OutputFolder'
#### DEVICE DISCOVERY #####
devicediscoveryv = configdict.get('DeviceDiscovery')
if devicediscoveryv == None:
	devicediscoveryv = 0
devicediscoveryseedv = configdict.get('DeviceDiscoverySeed')
devicediscoverysshv = configdict.get('DeviceDiscoverySSH')
if devicediscoverysshv == None:
	devicediscoverysshv = 0
devicediscoveryseedv = configdict.get('DeviceDiscoverySeed')
if devicediscoveryseedv == None:
	print 'No CDP seed router, not doing CDP/LLDP discovery'
	devicediscoveryseedv = 'NA'
devicediscoverydepthv = configdict.get('DeviceDiscoveryDepth')
if devicediscoverydepthv == None:
	devicediscoverydepthv = 0
devicediscoverysshtypev = configdict.get('DeviceDiscoverySSHType')
devicediscoverysshtypev = devicediscoverysshtypev.lower()
if devicediscoverysshtypev == None:
	devicediscoverysshtypev = 'ios'
if 'nxos' in devicediscoverysshtypev.lower() or 'ios' in devicediscoverysshtypev.lower() or 'xe' in devicediscoverysshtypev.lower():
	devicediscoverysshtypev = devicediscoverysshtypev.encode('utf-8')
	if not 'cisco' in devicediscoverysshtypev:
		devicediscoverysshtypev = 'cisco_' + devicediscoverysshtypev
#### MNET CDP DISCOVERY ####
devicediscoverymapv = configdict.get('DeviceDiscoveryMap')
if devicediscoverymapv == None:
	devicediscoverymapv = 0
devicediscoveryincludephones = configdict.get('DeviceDiscoveryIncludePhones')
if devicediscoveryincludephones == None or devicediscoveryincludephones == False:
	devicediscoveryincludephones = 0
else:
	devicediscoveryincludephones = 1
devicediscoverymaptitlev = configdict.get('DeviceDiscoveryMapTitle')
if devicediscoverymaptitlev == None:
	devicediscoverymaptitlev = 'Network Topology'
if devicediscoverymapv == 1:
	import pydot
	pydottest = pydot.find_graphviz()
	try:
		if not 'neato' in pydottest:
			print 'Could not find graphviz. Please make sure the PATH variable is set in windows to the correct location, and that the product is installed'
	except:
		print 'Could not find graphviz. Please make sure the PATH variable is set in windows to the correct location, and that the product is installed'
mnetvar = {}
mnetsnmp = []
mnetdomains = []
excludedsubnets = []
includedsubnets = []
mnetgraph = {}
# MNET SNMP
for snmpvariables in xlhelper.sheet_to_dict(excelfilelocation,'SNMP'):
	snmpdict = {}
	try:
		snmpcommunityv = snmpvariables.get('SNMP Community').encode('utf-8')
		snmpversionv = snmpvariables.get('Version').encode('utf-8')
	except:
		snmpcommunityv = snmpvariables.get('SNMP Community')
		snmpversionv = snmpvariables.get('Version')
	try:
		snmpdict['community'] = snmpcommunityv
		snmpdict['ver'] = snmpversionv
		mnetsnmp.append(snmpdict)
	except:
		devicediscoverysnmp = 'NA'
# MNET DOMAINS
devicediscoverydomains = configdict.get('DeviceDiscoveryDomains')
if devicediscoverydomains == None:
	devicediscoverydomains = 'NA'
if ',' in devicediscoverydomains:
	devicediscoverydomains = devicediscoverydomains.split(',')
	for device in devicediscoverydomains:
		mnetdomains.append(device)
else:
	mnetdomains.append(devicediscoverydomains)
# MNET Exclude
devicediscoveryexcludedsubnets = configdict.get('DeviceDiscoveryExcludedSubnets')
if devicediscoveryexcludedsubnets == None:
	devicediscoveryexcludedsubnets = '255.255.255.255/32'
if ',' in devicediscoveryexcludedsubnets:
	devicediscoveryexcludedsubnets = devicediscoveryexcludedsubnets.split(',')
	for device in devicediscoveryexcludedsubnets:
		excludedsubnets.append(device)
else:
	excludedsubnets.append(devicediscoveryexcludedsubnets)
# MNET Subnets
devicediscoveryincludedsubnets = configdict.get('DeviceDiscoveryIncludedSubnets')
if devicediscoveryincludedsubnets == None:
	devicediscoveryincludedsubnets = '10.0.0.0/8,192.168.0.0/16,172.16.0.0/12'
if ',' in devicediscoveryincludedsubnets:
	devicediscoveryincludedsubnets = devicediscoveryincludedsubnets.split(',')
	for device in devicediscoveryincludedsubnets:
		includedsubnets.append(device)
else:
	includedsubnets.append(devicediscoveryincludedsubnets)
# MNET Graph
mnetgraph['node_text_size'] = 10
mnetgraph['link_text_size'] = 9
mnetgraph['title_text_size'] = 15
mnetgraph['include_svi'] = 1
mnetgraph['include_lo'] = 1
mnetgraph['include_serials'] = 1
mnetgraph['get_stack_members'] = 1
mnetgraph['get_vss_members'] = 1
mnetgraph['expand_stackwise'] = 0
mnetgraph['expand_vss'] = 0
mnetgraph['expand_lag'] = 0
# MNET Full
mnetvar['snmp'] = mnetsnmp
mnetvar['domains'] = mnetdomains
mnetvar['exclude'] = excludedsubnets
mnetvar['subnets'] = includedsubnets
mnetvar['graph'] = mnetgraph
mnetvar['exclude_hosts'] = []
mnetvar['include_phones'] = devicediscoveryincludephones
mnetfile = 'nda-mnetvar.conf'
mnetcat = 'nda-mnetcat.csv'
with open(mnetfile,'w') as jsonfile:
	json.dump(mnetvar, jsonfile)
tempfilelist.append(mnetfile)
tempfilelist.append(mnetcat)
##### MNET END #####
# Normal Config Vars	
configurationv = configdict.get('Configuration')
if configurationv == None:
	configurationv = True
healthcheckv = configdict.get('HealthCheck')
if healthcheckv == None:
	healthcheckv = True
fullinventoryreportv = configdict.get('FullInventoryReport')
if fullinventoryreportv == None:
	fullinventoryreportv = True
interfacereportv = configdict.get('InterfaceReport')
if interfacereportv == None:
	interfacereportv = True
arpmacreportv = configdict.get('ARPMACReport')
if arpmacreportv == None:
	arpmacreportv = True
poereportv = configdict.get('POEReport')
if poereportv == None:
	poereportv = True

# End of Config Variables

##### NDA Specific Functions #####
def startalltests(sshdevice,usernamelist,exportlocation):
	if configurationv == 1:
		fullinventorylistr,ipmactablelistr,mactablelistr,iparptablelistr,l2interfacelistr,l3interfacelistr,poeinterfacelistr = gatherdata(sshdevice,usernamelist,exportlocation)
		for fullinv in fullinventorylistr:
			fullinventorylist.append(fullinv)
		for ipmac in ipmactablelistr:
			ipmactablelist.append(ipmac)
		for mactable in mactablelistr:
			mactablelist.append(mactable)
		for iparp in iparptablelistr:
			iparptablelist.append(iparp)
		for l2int in l2interfacelistr:
			l2interfacelist.append(l2int)
		for l3int in l3interfacelistr:
			l3interfacelist.append(l3int)
		for poeint in poeinterfacelistr:
			poeinterfacelist.append(poeint)
	if healthcheckv == 1:
		healthcheckreturn = healthcheck(sshdevice,usernamelist,exportlocation)
		if healthcheckreturn != False:
			for health in healthcheckreturn:
				healthchecklist.append(health)
	sys.exit()

##### END OF FUNCTIONS #####				


# Start of threading
print '----Starting to gather data from equipment----'
if __name__ == "__main__":
	# Get Devices from XLSX and lowercase it all
	for xlsxdevices in xlhelper.sheet_to_dict(excelfilelocation,'Device IPs'):
		try:
			xlsxdeviceslist = {}
			xlsxdeviceslist['Device IPs'] = xlsxdevices.get('Device IPs').encode('utf-8').lower()
			xlsxdeviceslist['Vendor'] = xlsxdevices.get('Vendor').encode('utf-8').lower()
			xlsxdeviceslist['Type'] = xlsxdevices.get('Type').encode('utf-8').lower()
			sshdevices.append(xlsxdeviceslist)
		except:
			pass
	# Get Devices from CDP and check to ignore duplicates imported from XLSX
	if devicediscoveryv == 1 and not 'na' in devicediscoveryseedv.lower():
		# SNMP Section
		graph = mnetsuite_routeallthings.mnet_graph()
		opt_dot = None
		opt_depth = devicediscoverydepthv
		opt_title = devicediscoverymaptitlev
		opt_conf = mnetfile
		opt_catalog = mnetcat
		graph.set_max_depth(opt_depth)
		graph.load_config(mnetfile)
		graph.crawl(devicediscoveryseedv)
		graph.output_catalog(mnetcat)
		# null byte check
		mnetcatfile = open(mnetcat, 'rb')
		mnetcatdata = mnetcatfile.read()
		if not mnetcatdata.find('\x00') == 1:
			mnetcatfilew = open(mnetcat, 'wb')
			mnetcatfilew.write(mnetcatdata.replace('\x00', ''))
			mnetcatfilew.close()
			mnetcatfile.close()
			mnetcatfile = open (mnetcat, 'rb')
		mnetcatalog = csv.reader(mnetcatfile, delimiter=',')
		for row in mnetcatalog:
			try:
				# Point based system to match devices
				skipimport = 0
				ciscopoints = 0
				hppoints = 0
				# Missing IP
				if row[1] == '':
					ciscopoints = ciscopoints - 50
					hppoints = hppoints - 50
				# See if match in version or boot image
				if row[6] != 'None':
					ciscopoints = ciscopoints + 5
				if re.match(ciscoverreg, row[3]):
					ciscopoints = ciscopoints + 5
				if re.match(nxosverreg, row[3]):
					ciscopoints = ciscopoints + 5
				# See if model is in list of IPs to match Cisco
				if any(word in row[2] for word in ciscoxelist):
					ciscopoints = ciscopoints + 5
				if any(word in row[2] for word in ciscoioslist):
					ciscopoints = ciscopoints + 5
				if any(word in row[2] for word in cisconxoslist):
					ciscopoints = ciscopoints + 5
				# See if HP			
				if re.match(hpproductreg, row[2]):
					hppoints = hppoints + 5
				# Check point total for Cisco match
				if ciscopoints > 4 and ciscopoints > hppoints:
					snmpdiscoverylist = {}
					snmpdeviceip = snmpdiscoverylist['Device IPs'] = row[1]
					if not IP_ADDRESS.match(snmpdeviceip):
						skipimport = 1
					snmpdiscoverylist['Device IPs'] = snmpdeviceip
					snmpdiscoverylist['Vendor'] = 'Cisco'
					# Check for device type logic
					if any(word in row[2] for word in ciscoxelist):
						snmpdiscoverydevicetype = 'xe'
					if any(word in row[2] for word in ciscoioslist):
						snmpdiscoverydevicetype = 'ios'
					if any(word in row[2] for word in cisconxoslist):
						snmpdiscoverydevicetype = 'nxos'
					snmpdiscoverylist['Type'] = snmpdiscoverydevicetype
					snmpduplicate = 0
					for sshdevice in sshdevices:
						try:
							if snmpdeviceip == sshdevice.get('Device IPs').encode('utf-8'):
								snmpduplicate = 1
						except:
							pass
					if snmpduplicate == 0 and skipimport == 0:
						sshdevices.append(snmpdiscoverylist)
					continue
				if hppoints > 4 and hppoints > ciscopoints:
					snmpdiscoverylist = {}
					snmpdeviceip = snmpdiscoverylist['Device IPs'] = row[1]
					if not IP_ADDRESS.match(snmpdeviceip):
						skipimport = 1
					snmpdiscoverylist['Device IPs'] = snmpdeviceip
					snmpdiscoverylist['Vendor'] = 'HP'
					# Check for device type logic
					snmpdiscoverydevicetype = 'procurve'
					snmpdiscoverylist['Type'] = snmpdiscoverydevicetype
					snmpduplicate = 0
					for sshdevice in sshdevices:
						try:
							if snmpdeviceip == sshdevice.get('Device IPs').encode('utf-8'):
								snmpduplicate = 1
						except:
							pass
					if snmpduplicate == 0 and skipimport == 0:
						sshdevices.append(snmpdiscoverylist)
					continue
			except:
				pass
		mnetcatfile.close()
	# SSH Section
	if devicediscoverysshv == 1:
		print 'Starting SSH CDP Discovery'
		cdpdevicecomplete = cdpdiscovery(usernamelist,devicediscoveryseedv,devicediscoverysshtypev,devicediscoverydepthv,includedsubnets,excludedsubnets)
		if cdpdevicecomplete:
			for cdpdevice in cdpdevicecomplete:
				cdpduplicate = 0
				cdpdeviceip = cdpdevice.get('Device IPs').encode('utf-8')
				for sshdevice in sshdevices:
					try:
						if cdpdeviceip == sshdevice.get('Device IPs').encode('utf-8'):
							cdpduplicate = 1
					except:
						pass
				if cdpduplicate == 0:
					sshdevices.append(cdpdevice)
	# Start Threads
	
	main_thread = threading.currentThread()
	
	for sshdevice in sshdevices:	
		sshdeviceip = sshdevice.get('Device IPs').encode('utf-8')
		sshdevicetype = sshdevice.get('Type').encode('utf-8')
		
		# Run Cisco Tests
		if 'ios' in sshdevicetype.lower() or 'xe' in sshdevicetype.lower() or 'nxos' in sshdevicetype.lower():
			print "Spawning Thread for " + sshdeviceip
			t = threading.Thread(target=startalltests, args=(sshdevice,usernamelist,exportlocation))
			t.daemon = True
			t.start()
			time.sleep(5)
	runningthreads = True
	maxtimeout = 900
	second = 0
	while runningthreads == True:
		if second > maxtimeout:
			runningthreads = False
			print 'Exiting due to maximum timeout reached. If this is due to the quantity of devices, please increase your timeout value. Currently its ' + str(maxtimeout) + '.' 
		if threading.activeCount() == 1:
			runningthreads = False
		time.sleep(1)
		second = second + 1

# Map Output
print 'Starting to export Map Topology'
try:
	if devicediscoverymapv == 1 and devicediscoveryv == 1:
		topologyfile = exportlocation + '\\Network_Topology.pdf'
		topologyfiledot = exportlocation + '\\Network_Topology.dot'
		topologyname = devicediscoverymaptitlev
		graph.output_dot(topologyfile, topologyname)
		graph.output_dot(topologyfiledot, topologyname)
except Exception as e:
	print 'Error with exporting network topology. Error is ' + str(e)

# Report Outputs
if fullinventoryreportv == 1:
	print 'Exporting Full Inventory Report'
	fullinventoryreport(fullinventorylist,exportlocation)
if interfacereportv == 1:
	print 'Exporting Interface Report'
	interfacereport(l2interfacelist,l3interfacelist,poeinterfacelist,exportlocation)
if poereportv == 1:
	print 'Exporting POE Report'
	poereport(poeinterfacelist,exportlocation)
if healthcheckv == 1:
	print 'Exporting Health Report'
	healthcheckreport(healthchecklist,exportlocation)
if arpmacreportv == 1:
	print 'Exporting ARP/MAC Report'
	arpmacreport(iparptablelist,ipmactablelist,mactablelist,exportlocation)
	
# Cleanup
print 'Starting Temp File Cleanup'
for file in tempfilelist:
	try:
		os.remove(file)
	except:
		pass
		