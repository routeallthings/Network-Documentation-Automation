#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# downloadfile.py

import requests

def downloadfile(url,saveas):
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(saveas, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)