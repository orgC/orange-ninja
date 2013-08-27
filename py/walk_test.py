#!/usr/local/bin/python

import os

path='/root/HSGW-2.0'

path_array = []

for root, dirs, files in os.walk(path):
	for each_dir in dirs:
		if '.svn' in dirs:
			dirs.remove('.svn')

	for each_file in files:
		print '%s/%s' % (root, each_file)
	

