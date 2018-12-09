#!/usr/bin/env python

# ---AUTHOR---
# Name: Matt Cross
# Email: routeallthings@gmail.com
#
# copytree.py

# Native Modules
import os
import shutil

def copytree(src, dst, symlinks=False, ignore=None):
	for src_dir, dirs, files in os.walk(src):
		dst_dir = src_dir.replace(src, dst, 1)
		if not os.path.exists(dst_dir):
			os.makedirs(dst_dir)
		for file_ in files:
			src_file = os.path.join(src_dir, file_)
			dst_file = os.path.join(dst_dir, file_)
			if os.path.exists(dst_file):
				# in case of the src and dst are the same file
				os.remove(dst_file)
			shutil.move(src_file, dst_dir)