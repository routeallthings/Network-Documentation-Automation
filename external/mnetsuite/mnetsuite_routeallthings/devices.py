#!/usr/bin/python

# Mnetsuite Addition (Device SNMP)

try:
	if modelvendor == None:
		modelvendor = 'cisco_ios'
except:
	modelvendor = 'cisco_ios'

if modelvendor == 'cisco_ios' or modelvendor == 'cisco_xe':
	# IOS
	OID_SYSNAME		= '1.3.6.1.2.1.1.5.0'

	OID_SYS_SERIAL	= '1.3.6.1.4.1.9.3.6.3.0'
	OID_SYS_BOOT	= '1.3.6.1.4.1.9.2.1.73.0'

	OID_IFNAME		= '1.3.6.1.2.1.31.1.1.1.1'				# + ifidx (BULK)

	OID_CDP			= '1.3.6.1.4.1.9.9.23.1.2.1.1'			# (BULK)
	OID_CDP_IPADDR	= '1.3.6.1.4.1.9.9.23.1.2.1.1.4'
	OID_CDP_IOS		= '1.3.6.1.4.1.9.9.23.1.2.1.1.5'
	OID_CDP_DEVID	= '1.3.6.1.4.1.9.9.23.1.2.1.1.6'		# + .ifidx.53
	OID_CDP_DEVPORT	= '1.3.6.1.4.1.9.9.23.1.2.1.1.7'
	OID_CDP_DEVPLAT	= '1.3.6.1.4.1.9.9.23.1.2.1.1.8'
	OID_CDP_INT		= '1.3.6.1.4.1.9.9.23.1.1.1.1.'			# 6.ifidx

	OID_LLDP	     = '1.0.8802.1.1.2.1.4'
	OID_LLDP_TYPE    = '1.0.8802.1.1.2.1.4.1.1.4.0'
	OID_LLDP_DEVID   = '1.0.8802.1.1.2.1.4.1.1.5.0'
	OID_LLDP_DEVPORT = '1.0.8802.1.1.2.1.4.1.1.7.0'
	OID_LLDP_DEVNAME = '1.0.8802.1.1.2.1.4.1.1.9.0'
	OID_LLDP_DEVDESC = '1.0.8802.1.1.2.1.4.1.1.10.0'
	OID_LLDP_DEVADDR = '1.0.8802.1.1.2.1.4.2.1.5.0'

	OID_TRUNK_ALLOW  = '1.3.6.1.4.1.9.9.46.1.6.1.1.4'		# + ifidx (Allowed VLANs)
	OID_TRUNK_NATIVE = '1.3.6.1.4.1.9.9.46.1.6.1.1.5'		# + ifidx (Native VLAN)
	OID_TRUNK_VTP	 = '1.3.6.1.4.1.9.9.46.1.6.1.1.14'		# + ifidx (VTP Status)
	OID_LAG_LACP	 = '1.2.840.10006.300.43.1.2.1.1.12'	# + ifidx (BULK)

	OID_IP_ROUTING	= '1.3.6.1.2.1.4.1.0'
	OID_IF_VLAN		= '1.3.6.1.4.1.9.9.68.1.2.2.1.2'		# + ifidx (BULK)

	OID_IF_IP		= '1.3.6.1.2.1.4.20.1'					# (BULK)
	OID_IF_IP_ADDR	= '1.3.6.1.2.1.4.20.1.2'				# + a.b.c.d = ifid
	OID_IF_IP_NETM	= '1.3.6.1.2.1.4.20.1.3.'				# + a.b.c.d

	OID_SVI_VLANIF	= '1.3.6.1.4.1.9.9.128.1.1.1.1.3'		# cviRoutedVlanIfIndex

	OID_ETH_IF		= '1.3.6.1.2.1.2.2.1'					# ifEntry
	OID_ETH_IF_TYPE	= '1.3.6.1.2.1.2.2.1.3'					# ifEntry.ifType	24=loopback
	OID_ETH_IF_DESC	= '1.3.6.1.2.1.2.2.1.2'					# ifEntry.ifDescr

	OID_OSPF		= '1.3.6.1.2.1.14.1.2.0'
	OID_OSPF_ID		= '1.3.6.1.2.1.14.1.1.0'

	OID_BGP_LAS		= '1.3.6.1.2.1.15.2.0'

	OID_HSRP_PRI	= '1.3.6.1.4.1.9.9.106.1.2.1.1.3.1.10'
	OID_HSRP_VIP	= '1.3.6.1.4.1.9.9.106.1.2.1.1.11.1.10'

	OID_STACK		= '1.3.6.1.4.1.9.9.500'
	OID_STACK_NUM	= '1.3.6.1.4.1.9.9.500.1.2.1.1.1'
	OID_STACK_ROLE	= '1.3.6.1.4.1.9.9.500.1.2.1.1.3'
	OID_STACK_PRI	= '1.3.6.1.4.1.9.9.500.1.2.1.1.4'
	OID_STACK_MAC	= '1.3.6.1.4.1.9.9.500.1.2.1.1.7'
	OID_STACK_IMG	= '1.3.6.1.4.1.9.9.500.1.2.1.1.8'

	OID_VSS_MODULES = '1.3.6.1.4.1.9.9.388.1.4.1.1.1'		# .modidx = 1
	OID_VSS_MODE	= '1.3.6.1.4.1.9.9.388.1.1.4.0'
	OID_VSS_DOMAIN	= '1.3.6.1.4.1.9.9.388.1.1.1.0'

	OID_ENTPHYENTRY_CLASS    = '1.3.6.1.2.1.47.1.1.1.1.5'		# + .modifx (3=chassis) (9=module)
	OID_ENTPHYENTRY_SOFTWARE = '1.3.6.1.2.1.47.1.1.1.1.9'		# + .modidx
	OID_ENTPHYENTRY_SERIAL   = '1.3.6.1.2.1.47.1.1.1.1.11'		# + .modidx
	OID_ENTPHYENTRY_PLAT     = '1.3.6.1.2.1.47.1.1.1.1.13'		# + .modidx

	# mnet-tracemac
	OID_VLANS			= '1.3.6.1.4.1.9.9.46.1.3.1.1.2'
	OID_VLAN_CAM		= '1.3.6.1.2.1.17.4.3.1.1'

	OID_BRIDGE_PORTNUMS	= '1.3.6.1.2.1.17.4.3.1.2'
	OID_IFINDEX			= '1.3.6.1.2.1.17.1.4.1.2'

if modelvendor == 'cisco_nxos':
	# NXOS
	OID_SYSNAME	= '1.3.6.1.2.1.1.5.0'

	OID_SYS_SERIAL	= '1.3.6.1.2.1.47.1.1.1.1.11.149'
	OID_SYS_BOOT	= '1.3.6.1.4.1.9.9.25.1.1.1.2.3'

	OID_IFNAME		= '1.3.6.1.2.1.31.1.1.1.1'				# + ifidx (BULK)

	OID_CDP			= '1.3.6.1.4.1.9.9.23.1.2.1.1'			# (BULK)
	OID_CDP_IPADDR		= '1.3.6.1.4.1.9.9.23.1.2.1.1.4'
	OID_CDP_IOS		= '1.3.6.1.4.1.9.9.23.1.2.1.1.5'
	OID_CDP_DEVID	= '1.3.6.1.4.1.9.9.23.1.2.1.1.6'		# + .ifidx.53
	OID_CDP_DEVPORT	= '1.3.6.1.4.1.9.9.23.1.2.1.1.7'
	OID_CDP_DEVPLAT	= '1.3.6.1.4.1.9.9.23.1.2.1.1.8'
	OID_CDP_INT		= '1.3.6.1.4.1.9.9.23.1.1.1.1.'			# 6.ifidx

	OID_LLDP	     = '1.0.8802.1.1.2.1.4'
	OID_LLDP_TYPE    = '1.0.8802.1.1.2.1.4.1.1.4.0'
	OID_LLDP_DEVID   = '1.0.8802.1.1.2.1.4.1.1.5.0'
	OID_LLDP_DEVPORT = '1.0.8802.1.1.2.1.4.1.1.7.0'
	OID_LLDP_DEVNAME = '1.0.8802.1.1.2.1.4.1.1.9.0'
	OID_LLDP_DEVDESC = '1.0.8802.1.1.2.1.4.1.1.10.0'
	OID_LLDP_DEVADDR = '1.0.8802.1.1.2.1.4.2.1.5.0'

	OID_TRUNK_ALLOW  = '1.3.6.1.4.1.9.9.46.1.6.1.1.4'		# + ifidx (Allowed VLANs)
	OID_TRUNK_NATIVE = '1.3.6.1.4.1.9.9.46.1.6.1.1.5'		# + ifidx (Native VLAN)
	OID_TRUNK_VTP	 = '1.3.6.1.4.1.9.9.46.1.6.1.1.14'		# + ifidx (VTP Status)
	OID_LAG_LACP	 = '1.2.840.10006.300.43.1.2.1.1.12'	# + ifidx (BULK)

	OID_IP_ROUTING	= '1.3.6.1.2.1.4.1.0'
	OID_IF_VLAN		= '1.3.6.1.4.1.9.9.68.1.2.2.1.2'		# + ifidx (BULK)

	OID_IF_IP		= '1.3.6.1.2.1.4.20.1'					# (BULK)
	OID_IF_IP_ADDR	= '1.3.6.1.2.1.4.20.1.2'				# + a.b.c.d = ifid
	OID_IF_IP_NETM	= '1.3.6.1.2.1.4.20.1.3.'				# + a.b.c.d

	OID_SVI_VLANIF	= '1.3.6.1.4.1.9.9.128.1.1.1.1.3'		# cviRoutedVlanIfIndex

	OID_ETH_IF		= '1.3.6.1.2.1.2.2.1'					# ifEntry
	OID_ETH_IF_TYPE	= '1.3.6.1.2.1.2.2.1.3'					# ifEntry.ifType	24=loopback
	OID_ETH_IF_DESC	= '1.3.6.1.2.1.2.2.1.2'					# ifEntry.ifDescr

	OID_OSPF		= '1.3.6.1.2.1.14.1.2.0'
	OID_OSPF_ID		= '1.3.6.1.2.1.14.1.1.0'

	OID_BGP_LAS		= '1.3.6.1.2.1.15.2.0'

	OID_HSRP_PRI	= '1.3.6.1.4.1.9.9.106.1.2.1.1.3.1.10'
	OID_HSRP_VIP	= '1.3.6.1.4.1.9.9.106.1.2.1.1.11.1.10'

	OID_STACK		= '1.3.6.1.4.1.9.9.500'
	OID_STACK_NUM	= '1.3.6.1.4.1.9.9.500.1.2.1.1.1'
	OID_STACK_ROLE	= '1.3.6.1.4.1.9.9.500.1.2.1.1.3'
	OID_STACK_PRI	= '1.3.6.1.4.1.9.9.500.1.2.1.1.4'
	OID_STACK_MAC	= '1.3.6.1.4.1.9.9.500.1.2.1.1.7'
	OID_STACK_IMG	= '1.3.6.1.4.1.9.9.500.1.2.1.1.8'

	OID_VSS_MODULES = '1.3.6.1.4.1.9.9.388.1.4.1.1.1'		# .modidx = 1
	OID_VSS_MODE	= '1.3.6.1.4.1.9.9.388.1.1.4.0'
	OID_VSS_DOMAIN	= '1.3.6.1.4.1.9.9.388.1.1.1.0'

	OID_ENTPHYENTRY_CLASS    = '1.3.6.1.2.1.47.1.1.1.1.5'		# + .modifx (3=chassis) (9=module)
	OID_ENTPHYENTRY_SOFTWARE = '1.3.6.1.2.1.47.1.1.1.1.9'		# + .modidx
	OID_ENTPHYENTRY_SERIAL   = '1.3.6.1.2.1.47.1.1.1.1.11'		# + .modidx
	OID_ENTPHYENTRY_PLAT     = '1.3.6.1.2.1.47.1.1.1.1.13'		# + .modidx

	# mnet-tracemac
	OID_VLANS			= '1.3.6.1.4.1.9.9.46.1.3.1.1.2'
	OID_VLAN_CAM		= '1.3.6.1.2.1.17.4.3.1.1'

	OID_BRIDGE_PORTNUMS	= '1.3.6.1.2.1.17.4.3.1.2'
	OID_IFINDEX			= '1.3.6.1.2.1.17.1.4.1.2'

	OID_ERR			= 'No Such Object currently exists at this OID'
	OID_ERR_INST	= 'No Such Instance currently exists at this OID'