#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# ndavariables.py

# Native Modules
import re

# Global Variables

ipv4_address = re.compile('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')

#Creation of SSH commands

# Cisco IOS/XE
showrun = "show running-config"
showstart = "show startup-config"
showver = "show version"
showlic = "show license"
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
showinterfacet = "show interface transceiver"
showiparp = "show ip arp"
showmacaddress = "show mac address-table"
showmacaddress_older = "show mac-address-table"
showlocation = "show running-config | include ^snmp-server location"
showlicense = "show license"

# NXOS Specific
showpowerinline_nxos = "show environment power"
showtemp_nxos = "show env temperature"
showlocation_nxos = "show running-config | include '^snmp-server location'"
showinttrans = "show interface transceiver"

# Device Match Lists
ciscoxelist = '3650 3850 9300 9400 9500 4500 4431 4451 4321 4331 4351 asr'
ciscoioslist = '3750 2960 3560 6500 2801 2811 2821 2851 2911 2921 2951 2901 3825 3845'
cisconxoslist = '7700 7000 Nexus N5K N7K N3K N4K N6K N9K N77'

# Device Match Lists Convert
ciscoxelist = ciscoxelist.split(' ')
ciscoioslist = ciscoioslist.split(' ')
cisconxoslist = cisconxoslist.split(' ')

# Device Type Lists
switchlist = 'Catalyst 9300 9400 9500 2950 2960 3550 3560 3750 3650 3850 4500 6500 WS-C Nexus NXOS'
routerlist = '2801 2811 2821 2851 2901 2911 2921 2951 3825 3845 4300 4400 4321 4331 4351 4431 4451 asr csv'
fwlist = 'ASA'

# Device Type Convert
switchlist = switchlist.split(' ')
routerlist = routerlist.split(' ')
fwlist = fwlist.split(' ')

# Cisco IOS Version Number Regex
ciscoverreg = '1[256]\.[1-9]\(.*\).*'
nxosverreg = '[4-8].[0-9]\([0-9]\)'

# HP Product Number Regex
hpproductreg = re.compile('^[A-Z][0-9]{3}.*$')

# URLs to use
maclookupurl = 'http://macvendors.co/api/%s'
maclookupdburl = "http://standards-oui.ieee.org/oui.txt"

# Regex
IP_ADDRESS = re.compile("^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$")