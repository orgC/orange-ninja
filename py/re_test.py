#!/usr/bin/python

import os, re

str = "from Femal today a.c b.c xxx man xman abc ccc "

str1 = '/root/source/HACCG6.1/XuanWu'
strr = '/root/source/HACCG6.1'
str2 = '/test/abcd'

str1 = str1.replace('%s' % strr, '%s' % str2)

print str1


'''
str_list = str.split()

for each_one in str_list:
	#print "%s" % each_one
	p = re.compile(r'.*\.c$')
	m = p.match(each_one)
	#m = re.match(r'*.c', each_one)
	if m:
		print "found %s" % each_one
	else:
		print "not found"
	
'''

