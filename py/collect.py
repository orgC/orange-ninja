#!/usr/bin/python

from neo_common import log_info
from neo_common import ssh_connection

def flush_gcov(ip_addr, username, password, debug_flag):
	global g_debug
	try:
		testbed=ssh_connection(ip_addr, username, password, debug_on=debug_flag)
	except:
		log_info('Connect failed.')
		return
	try:
		testbed.set_prompt('% ')
		testbed.send_command('dtach -a /tmp/dtach-ha -e ^C', timeout=30)
		testbed.set_prompt('WinG% ')
		testbed.send_command('exit', timeout=1)
		testbed.clean_buff()
		log_buff = testbed.send_command('FlushGCover ', timeout=30)
		print log_buff
	except:
		testbed.disconnect()
		log_info('flush gcov failed.')

def main():
	debug_flag = 0
	flush_gcov('10.180.24.19', 'root', 'root', debug_flag)
	

if __name__ == '__main__':
	log_info('============= START ==============')
	main()
	log_info('=============THE END==============')



