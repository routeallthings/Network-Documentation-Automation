#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# ndagraph.py

# Import Modules
import pydot
import re
import time

def networkgraph(topologyfile,topologyname, networkgraphlist, fullinventorylist, l2interfacelist, l3interfacelist):
	# Create lists
	duplicatelink = []
	dupdetect = []
	# Pydot base configuration
	graph = pydot.Dot(graph_type='digraph')	
	# Create all primary network devices
	for device in networkgraphlist:
		# Get device information
		devicehostname = device['hostname']
		deviceipaddress = device['ip']
		# Duplicate detect
		for dupdev in dupdetect:
			if dupdev == devicehostname:
				continue
		# Get device model
		stackv = 0
		stackinv = []
		moduleinv = []
		deviceinv = filter(lambda x: x['Hostname'] == devicehostname, fullinventorylist)
		# Get Modules and add to inventory
		for modeldict in deviceinv:
			if re.match('.*\-NM\-.*',modeldict['Product ID']):
				try:
					modswitch = re.search('.*Switch (\d) .*',modeldict['Description']).group(1)
					modproductid = re.search('.*(NM\S+).*',modeldict['Product ID']).group(1)
					# Duplicate Detect
					moddup = 0
					for mod in moduleinv:
						if modswitch == mod['switch']:	
							moddup = 1
							break
					# Add if not duplicate
					if moddup == 0:	
						moduledict = {}
						moduledict['switch'] = modswitch
						moduledict['module'] = modproductid
						moduleinv.append(moduledict)
				except:
					continue
		# Get Chassis Information
		for modeldict in deviceinv:
			if re.match('.*[Cc]hassis$',modeldict['Description']):
				if modeldict['Stack Number'] == '':
					# Add module if one exists to chassis
					modelmodule = ''
					if moduleinv != []:
						for mod in moduleinv:
							modelmodule = mod['module']
					# Create full single chassis (including module)
					devicemodel = modeldict['Product ID'] + ' ' + modelmodule
					break
				else:
					# Detected multiple stack members
					stackv = 1
					# Find module if attached to stack member and add
					if 'switch' in modeldict['Stack Number'].lower():
						modswitch = re.search('.*Switch (\d).*',modeldict['Stack Number']).group(1)
					else:
						modswitch = modeldict['Stack Number']
					modmodulelist = filter(lambda x: x['switch'] == modswitch, moduleinv)
					modelmodule = ''
					if modmodulelist != []:
						for mod in modmodulelist:
							modelmodule = mod['module']
					if modelmodule != '':
						modelmodule = '[' + modelmodule + ']'
					stackinv.append('(' + modswitch + ') ' +  modeldict['Product ID'] + ' ' + modelmodule)
		if stackv == 1:
			# convert list of switches (if stacked) into a format for the label
			devicemodel = '\n'.join(stackinv)
		# Create device label
		devicelabel = devicehostname + '\n' + devicemodel + '\n' + 'ip:' + deviceipaddress
		# Add node to graph	
		node = pydot.Node(devicehostname, label=(devicelabel))
		graph.add_node(node)
		dupdetect.append(devicehostname)
		time.sleep(.1)
	# Create all secondary network devices
	for device in networkgraphlist:
		deviceneighborlist = device['neighbors']
		for neighbor in deviceneighborlist:
			deviceneighbor = neighbor['neighbor']
			sourceinterface = neighbor['sourceinterface']
			destinationinterface = neighbor['destinationinterface']
			deviceneighborip = neighbor['ip']
			deviceneighbordevice = neighbor['device']
			# Create secondary devices and attach information about them
			skipcreation = 0
			# Dup Detect
			for dupdev in dupdetect:
				if dupdev == deviceneighbor:
					skipcreation = 1
					break
			if skipcreation == 0:
				devicelabel = deviceneighbor + '\n' + deviceneighbordevice + '\n' + 'ip:' + deviceneighborip
				node = pydot.Node(deviceneighbor, label=(devicelabel))
				graph.add_node(node)
				dupdetect.append(deviceneighbor)
		time.sleep(.1)
	# Create all network device relationships
	for device in networkgraphlist:
		devicehostname = device['hostname']
		deviceneighborlist = device['neighbors']
		for neighbor in deviceneighborlist:
			deviceneighbor = neighbor['neighbor']
			sourceinterface = neighbor['sourceinterface']
			destinationinterface = neighbor['destinationinterface']
			deviceneighborip = neighbor['ip']
			deviceneighbordevice = neighbor['device']
			# Bidirectional link detection
			bidilinksource = filter(lambda x: x['source'] == deviceneighbor, duplicatelink)
			bidilinkdest = filter(lambda x: x['destination'] == devicehostname, bidilinksource)
			# if no bidirectional link found, create link
			if bidilinkdest == []:
				# Add link to duplicate list
				duplicatedict = {}
				duplicatedict['source'] = devicehostname
				duplicatedict['destination'] = deviceneighbor
				duplicatelink.append(duplicatedict)
				# Add edge node
				edge = pydot.Edge(devicehostname,deviceneighbor,color='#FF0000',label=('s:' + sourceinterface + '\n' + 'd:' + destinationinterface), fontcolor='#0000FF', fontsize=8)
				graph.add_edge(edge)
		time.sleep(.1)
	# Create final drawing
	graph.write_pdf(topologyfile)
			