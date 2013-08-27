#!/usr/bin/python
# Filename: collect_data.py
# debian  apt-get install python-pexpect 
import os, sys, time, re
from neo_common import log_info
from neo_common import ssh_connection

def config_testbed_hsgw(ip_addr, username, password, debug_flag):
    global g_debug
    try:
        testbed=ssh_connection(ip_addr, username, password, debug_on=debug_flag)
    except:
        log_info('Connect failed.')
        return
    try:
        testbed.send_command('killall hsgw', timeout=10)
        testbed.send_command('/etc/init.d/monit restart', timeout=10)
        testbed.send_command('export HW_PLATFORM=tc3k', timeout=5)
        testbed.set_prompt('system# ')
        testbed.send_command('su sysadmin', timeout=5)
        testbed.clean_buff()
        testbed.set_prompt('hsgw# ')
        testbed.send_command('set context=hsgw', timeout=30)
        testbed.send_command('set tm use-gxa=disabled', timeout=30)
        log_buff=testbed.send_command('show tm use-gxa', timeout=30)
        print log_buff
    except:
        testbed.disconnect()
        log_info('config_testbed_hsgw failed.')
    log_info('config_testbed_hsgw OK.')

def config_testbed_pgw(ip_addr, username, password, debug_flag):
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
        testbed.send_command('LMA DisableAuth', timeout=30)
        log_buff=testbed.send_command('LMA ShowConfiguration', timeout=30)
        print log_buff
    except:
        testbed.disconnect()
        log_info('config_testbed_pgw failed.')
    log_info('config_testbed_pgw OK.')

def config_checkone(ip_addr, username, password, debug_flag):
    global g_debug
    try:
        testbed=ssh_connection(ip_addr, username, password, debug_on=debug_flag)
    except:
        log_info('Connect failed.')
        return
    try:
        testbed.set_prompt('ue_simulator# ')
        testbed.send_command('cd /home/ue_simulator', timeout=30)
        log_buff=testbed.send_command('./checkone', timeout=30)
        print log_buff
    except:
        testbed.disconnect()
        log_info('config_ue_simulator failed.')
    log_info('config_ue_simulator OK.')

def config_ui_one_py(ip_addr, username, password, debug_flag):
    global g_debug
    try:
        testbed=ssh_connection(ip_addr, username, password, debug_on=debug_flag)
    except:
        log_info('Connect failed.')
        return
    try:
        testbed.set_prompt('binary# ')
        testbed.send_command(r'cd /home/ue_simulator/binary', timeout=30)
        log_buff=testbed.send_command(r'nohup ./ui_one.py /home/ue_simulator/binary >log_ui_one.txt 2>&1 &', timeout=30)
        log_buff=testbed.send_command(r'cat /home/ue_simulator/binary/log_ui_one.txt', timeout=30)
        print log_buff
    except:
        testbed.disconnect()
        log_info('config_ue_simulator failed.')
    log_info('config_ue_simulator OK.')

def config_dns_server(ip_addr, username, password, debug_flag):
    try:
        testbed=ssh_connection(ip_addr, username, password, debug_on=debug_flag)
    except:
        log_info('Connect failed.')
        return
    try:
        log_buff=testbed.send_command('ps -ef | grep named.conf', timeout=30)
        #root      6699     1  0 10:21 ?        00:00:00 /usr/local/named/sbin/named
        re_pid=re.search('root\s+(\d+)[^\r\n]+named\s+\-c',log_buff)
        if re_pid:
            testbed.send_command('kill -9 '+re_pid.group(1), timeout=30)
        testbed.send_command('nohup /usr/local/named/sbin/named -c /usr/local/named/etc/named.conf -g &', timeout=30)
        log_buff=testbed.send_command('ps -ef | grep named.conf', timeout=30)
        print log_buff
    except:
        testbed.disconnect()
        log_info('config_dns_server failed.')
    log_info('config_dns_server OK.')

def config_seagull(ip_addr, username, password, debug_flag):
    try:
        testbed=ssh_connection(ip_addr, username, password, debug_on=debug_flag)
    except:
        log_info('Connect failed.')
        return
    try:
        log_buff=testbed.send_command('ps -ef | grep seagull', timeout=30)
        #root     15378     1  0 10:58 ?        00:00:15 seagull -conf
        for seagull_pid in re.findall('root\s+(\d+)[^\r\n]+seagull\s+\-conf',log_buff):
            try:
                type(seagull_pid)
                testbed.send_command('kill -9 '+seagull_pid, timeout=30)
            except:
                pass
        testbed.set_prompt('run# ')
        testbed.send_command('cd /opt/seagull/diameter-env/run', timeout=30)
        testbed.send_command('./start_server_eap.ksh', timeout=30)
        testbed.send_command('./start_server_rf.ksh', timeout=30)
        testbed.send_command('./start_server_gxx_extern.ksh', timeout=30)
        log_buff=testbed.send_command('ps -ef | grep seagull', timeout=30)
        print log_buff
    except:
        testbed.disconnect()
        log_info('config_seagull failed.')
    log_info('config_seagull OK.')

def config_host_route(ip_addr, username, password, debug_flag):
    try:
        testbed=ssh_connection(ip_addr, username, password, debug_on=debug_flag)
    except:
        log_info('Connect failed.')
        return
    try:
        log_buff=testbed.send_command(r'nohup route -A inet6 add 3680:95::/60 gw 3600:105::95 &', timeout=30)
        log_buff=testbed.send_command(r'route -A inet6 -n', timeout=30)
        print log_buff
        log_buff=testbed.send_command(r'mount -t nfs 10.180.24.89:/home/ue_simulator /home/ue_simulator', timeout=30)
        log_buff=testbed.send_command(r'ls /home/ue_simulator/binary', timeout=30)
        print log_buff
    except:
        testbed.disconnect()
        log_info('config_host_route failed.')
    log_info('config_host_route OK.')

log_info('============= START ==============')
debug_flag=0

config_testbed_hsgw('10.180.24.94', 'root', 'pdg.net', debug_flag)
config_testbed_pgw ('10.180.24.95', 'root', 'pdg.net', debug_flag)
config_dns_server  ('10.180.24.95', 'root', 'pdg.net', debug_flag)
config_seagull     ('10.180.24.88', 'root', 'pdg.net', debug_flag)
config_host_route  ('10.180.24.88', 'root', 'pdg.net', debug_flag)
config_ui_one_py('10.180.24.89', 'root', 'pdg.net', debug_flag)
#config_checkone('10.180.24.89', 'root', 'pdg.net', debug_flag)

log_info('=============THE END==============')
