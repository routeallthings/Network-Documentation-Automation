#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# removeprefix.py

def removeprefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text