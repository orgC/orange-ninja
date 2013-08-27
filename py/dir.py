#!/usr/bin/python

import os


#list = os.listdir("../cover")
#for line in list:
#	print line


def exec_linux_cmd(cmd):
	r=os.popen(cmd)
	text=r.read()
	r.close()
	return text

log_dir = "log_%s" %datetime.datetime.now().strftime('%m%d-%H:%M:%S')
exec_linux_cmd("mkdir %s" %log_dir)
exec_linux_cmd("mv *.gcov %s" % log_dir)

