# Network Documentation Automation

The purpose of this tool is to pull information from the network via CDP/LLDP discovery or manual entry in XLSX. Please fill in the configuration tab on the templated print 'XLSX sheet, along with all the data that you want to test.

## Getting Started

You need to download and add configuration information into the included XLSX file. This data is what the script uses to run.

Step 1. Install Python 2.7
Step 2. Fill in the XLSX spreadsheet
Step 3. Run the script and reference the files

Report any issues to my email and I will get them fixed.

### Prerequisites

XLHELPER
OPENPYXL
REQUESTS

## Deployment

Configure the XLSX file (change only the values). After that just execute the script and answer the question.

## Features
- CDP/LLDP Discovery and/or Manual Entry (Using XLSX)
- Inventory
- Health Check
- Network Topology Mapping (Only for CDP/LLDP discovered devices currently)

## *Caveats
- Cisco IOS/XE/NXOS only as of right now, will add in other vendors as I get the features fleshed out.

## Versioning

VERSION 0.6.3


## Authors

* **Matt Cross** - [RouteAllThings](https://github.com/routeallthings)

See also the list of [contributors](https://github.com/routeallthings/Network-Documentation-Automation/contributors) who participated in this project.

## License

This project is licensed under the GNU - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to HBS for giving me a reason to write this.
* mnetsuite (fantastic package written by Michael Laforest (https://github.com/MJL85)).
* Netmiko
