# Network Documentation Automation

The purpose of this tool is to pull information from the network via CDP/LLDP discovery or manual entry in XLSX. Please fill in the configuration tab on the templated print 'XLSX sheet, along with all the data that you want to test.

## Getting Started

Look at the example files. In the XLSX spreadsheet, the columns are treated as separate datasets. The rows do not need to align.

Step 1. Fill in the data according to the column header. Use the interface name (vlan 20) for all source interfaces.
Step 2. Run the Python script and specify the output folder. 
Step 3. Run and profit

Report any issues to my email and I will get them fixed.

### Prerequisites

GIT (This is required to download the XLHELPER module using a fork that I modified for compatibility with Python 2.7)
XLHELPER
OPENPYXL
MNETSUITE (My local fork)


## Deployment

Configure the XLSX file (change only the values). After that just execute the script and answer the question.

## Features
- CDP/LLDP Discovery and/or Manual Entry (Using XLSX)
- Inventory
- Health Check
- Network Topology Mapping (Only for CDP/LLDP discovered devices currently)

## *Caveats
- Cisco only as of right now, will add in other vendors as I get the features fleshed out.

## Versioning

VERSION 0.5


## Authors

* **Matt Cross** - [RouteAllThings](https://github.com/routeallthings)

See also the list of [contributors](https://github.com/routeallthings/Network-Documentation-Automation/contributors) who participated in this project.

## License

This project is licensed under the GNU - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to HBS for giving me a reason to write this.
* mnetsuite (fantastic package written by Michael Laforest (https://github.com/MJL85)).
* Netmiko
