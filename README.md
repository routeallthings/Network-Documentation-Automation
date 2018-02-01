# Device Validator

The goal of this script was to be able to take XLSX data and validate switch configuration and access, health, and run some failover testing on the device.

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

## Deployment

Just execute the script and answer the questions

## Features
- XLSX-based validation script

## *Caveats
- None

## Versioning

VERSION 1.0


## Authors

* **Matt Cross** - [RouteAllThings](https://github.com/routeallthings)

See also the list of [contributors](https://github.com/routeallthings/Config-Creator/contributors) who participated in this project.

## License

This project is licensed under the GNU - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to HBS for giving me a reason to write this.
