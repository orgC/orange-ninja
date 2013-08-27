#!/usr/bin/python
import os, datetime, time, re, sys
import commands
import pexpect

def log_info(str_trace):
    '''print "\033[32m%s%20s:%03d %s\033[0m" %(datetime.datetime.now().strftime('%m%d-%H:%M:%S.%f'),
        sys._getframe().f_back.f_code.co_name,
        sys._getframe().f_back.f_lineno,
        str_trace);'''
    print "\033[32m%s%20s:%03d %s\033[0m" %(datetime.datetime.now(),
        sys._getframe().f_back.f_code.co_name,
        sys._getframe().f_back.f_lineno,
        str_trace);

def exec_linux_cmd(cmd):
    r=os.popen(cmd)
    text=r.read()
    r.close()
    return text

class ssh_connection(object):
    def __init__(self, host, username, password, debug_on=1):
        self.str_prompt = '# '
        self.ssh_handle=pexpect.spawn('ssh '+username+'@'+host)
        if 'pdg.net'==debug_on:
            self.ssh_handle.logfile=sys.stdout
        for loop in range(1,8):
            exp_index = self.ssh_handle.expect ([
                'yes/no',                                    # 0  If added new line here, please notice
                'password',                                  # 1  the index is used in the if elif lines.
                 '#',                                        # 2
                'Permission denied, please try again.',      # 3
                pexpect.TIMEOUT,                             # 4
                'Connection closed by UNKNOWN',              # 5
                pexpect.EOF], timeout=6)                     # 6
            if   0 == exp_index:
                self.ssh_handle.sendline('yes')
            elif 1 == exp_index:
                self.ssh_handle.sendline(password)
            elif 2 == exp_index:
                if 1==debug_on:
                    self.ssh_handle.logfile=sys.stdout
                self.clean_buff()
                log_info('ssh connect successfully.')
                return
            elif 3 == exp_index and 4 == exp_index:
                pass
            else:
                log_info('ssh connect failed.')
                self.ssh_handle.close(force=True)

    def set_prompt(self, str_prompt):
        self.str_prompt = str_prompt

    def clean_buff(self):
        for loop in range(1,3):
            exp_index=self.ssh_handle.expect([self.str_prompt, pexpect.TIMEOUT, pexpect.EOF], 0.01)
            if   2 == exp_index:
                log_info('expect EOF. what happened?')
                self.ssh_handle.close(force=True)

    def send_command(self, str_command, timeout=1):
        match_cmd = re.search('\w+', str_command)
        if not match_cmd:
            self.ssh_handle.sendline(str_command)
            return
        str_cmd_pattern=match_cmd.group()
        for resend in range(1,4):
            str_buffer = ''
            log_info('try %d timeout %d command [%s]' %(resend,timeout,str_command))
            self.ssh_handle.sendline(str_command)
            for loop in range(1,10):
                if loop > 1:
                    timeout=1
                exp_index=self.ssh_handle.expect([self.str_prompt, pexpect.TIMEOUT, pexpect.EOF], timeout)
                str_buffer+=self.ssh_handle.before
                if   0 == exp_index:
                    break
                elif 1 == exp_index:
                    log_info('TIMEOUT. Need longer timeout value. adding %d sec timeout' %loop)
                elif 2 == exp_index:
                    log_info('expect EOF. what happened?')
                    self.ssh_handle.close(force=True)
            match_result = re.search(str_cmd_pattern, str_buffer)
            if match_result:
                return str_buffer
            else:
                log_info('SEND COMMAND FAILED'+str_buffer)
        log_info('send command failed')
        self.ssh_handle.close(force=True)
        sys.exit()

    def disconnect(self):
        self.ssh_handle.close(force=True)


def flush_gcov(handle):
    try:
        handle.clean_buff()
        log_buff = handle.send_command('FlushGCover ', timeout=30)
        print log_buff
    except:
        handle.disconnect()
        log_info('flush gcov failed.')

def del_gcda(handle, path):
    try:
        handle.set_prompt('#')
        handle.send_command("find %s -name '*.gcda' | xargs rm " % path)
    except:
        handle.disconnect()
        log_info('delete gcda files failed.')

def get_gcda(sut_ip, sut_user, sut_passwd, sut_path, lo_path, case_id):
    # on 10.180.24.94 run ssh-copy-id -i  ~/.ssh/id_rsa.pub root@10.180.24.120
    # so, without passwd scp from 94 to 120
    log_info("get_gcda:  scp -r %s@%s:%s %s/%s" % (sut_user, sut_ip, sut_path, lo_path, case_id))
    scp_handle = pexpect.spawn('scp -r %s@%s:%s %s/%s' % (sut_user, sut_ip, sut_path, lo_path, case_id))
    while True:
        i=scp_handle.expect(['yes/no', 'password:', 'gcda', pexpect.EOF, pexpect.TIMEOUT], 1)
        if i==0:
            scp_handle.sendline('yes')
        if i==1:
            scp_handle.sendline(sut_passwd)
        elif i==2:
            pass
        elif i==3:
            break
        elif i==4:
            break
    #exec_linux_cmd('nohup scp -r %s@%s:%s %s/%s &' %(sut_user, sut_ip, sut_path, lo_path, case_id))

def send_to_remote(re_user, re_passwd, re_addr, lo_file):
    log_info("send_to_remote:   scp -r %s %s@%s" % (lo_file, re_user, re_addr))
    scp_handle = pexpect.spawn('scp -r %s %s@%s' % (lo_file, re_user, re_addr))
    while True:
        i=scp_handle.expect(['yes/no', 'password:', pexpect.EOF, pexpect.TIMEOUT], 1)
        if i==0:
            scp_handle.sendline('yes')
        if i==1:
            scp_handle.sendline(re_passwd)
        elif i==2:
            break
        elif i==3:
            break
    #exec_linux_cmd('nohup scp -r %s@%s:%s %s/%s &' %(sut_user, sut_ip, sut_path, lo_path, case_id))

def main():
    sut_ip          = '10.180.25.234'
    user          = 'root'
    password      = 'pdg.net'
    #password2     = 'root'
    #sut_prj_path = '/root/source/HACCG-6.1'

    rts_ip       = '10.180.24.120'
    rts_user     = 'root'
    rts_passwd   = 'root'
    
    sut_prj_path = '/home/thomas/HSGW-2.0.3-904'
    sut_tmp_prj_path = '/tmp/HSGW-2.0.3-904'
    rts_server_addr = '10.180.24.120:/opt/rts_gcov_log'
    local_gcda_path = '/opt/cts/gcda_tmp'
#    rts_server_addr = '/opt/rts_gcov_log/%s-%s' % \
#                        (os.path.basename(sut_prj_path), datetime.datetime.now().strftime('%m%d-%H%M'))

    #connect to testbed to create directory 
    '''
    rts_handle = ssh_connection(rts_ip, rts_user, rts_passwd, 0)
    try:
        rts_handle.send_command('mkdir -p %s', rts_server_addr)
        log_info("create directory %s success" % rts_server_addr)
    except:
        rts_handle.disconnect()
        log_info("create directory %s failed" % rts_server_addr)
        log_info('ssh unexpected exit!')
        sys.exit(0)
    rts_handle.disconnect()
    '''
    
    #create ssh handle, which connect with SUT. 
    handle=ssh_connection(sut_ip, user, password, 0)
    try:
        #replace below section according to the actual situation. 
        handle.set_prompt('% ')
        # This is for haccg
        #handle.send_command('dtach -a /tmp/dtach-ha -e ^C', timeout=30)
        # for HSGW
        handle.send_command('dtach -a /tmp/dtach-hsgw -e ^C', timeout=30)
        handle.set_prompt('WinG% ')
        flush_gcov(handle)
        handle.set_prompt('#')
        handle.send_command('\3\n', timeout=2)
        handle.clean_buff()
        case_dir = '%s__%s__%s' %(sys.argv[1], sys.argv[2], time.time())
        print '======================================================'
        print '    rm -rf /tmp/%s' % sut_prj_path
        print '    mv %s /tmp' % sut_prj_path
        print '    nohup scp -r /tmp/%s %s/%s' % (sut_prj_path, rts_server_addr, case_dir)
        print '======================================================'
        handle.send_command('rm -rf /tmp/%s' % sut_prj_path)
        handle.send_command('mv %s /tmp' % sut_prj_path)
        handle.send_command('nohup scp -r /tmp/%s %s/%s' % (sut_prj_path, rts_server_addr, case_dir))

        #get gcda from blade to CTS
        get_gcda(sut_ip, user, password, sut_tmp_prj_path, local_gcda_path, case_dir)
        #send_to_remote(user, password, re_addr=rts_server_addr, lo_file=('%s/%s' % (local_gcda_path, case_dir)))
        local_file = '%s/%s' % (local_gcda_path, case_dir)
        send_to_remote(user, rts_passwd, re_addr=rts_server_addr, lo_file=local_file)
        #log_info('rm /tmp/HSGW-2.0 -rf')
        #handle.send_command('mv %s /tmp; ' %sut_prj_path)
        #handle.send_command('nohup scp -r /tmp/HSGW-2.0 %s/%s &' %(rts_server_addr, case_dir))
        #handle.send_command('scp -r /tmp/HSGW-2.0 %s/%s' %(rts_server_addr, case_dir))
    except:
        handle.disconnect()
        log_info('ssh unexpected exit!')
        sys.exit(0)
    handle.disconnect()

if __name__ == '__main__':
    log_info('============= START ==============')
    try:
        type(sys.argv[1]) and type(sys.argv[2])
    except:
        log_info('please give the load-name and case-id.')
        sys.exit(0)
    main()
    log_info('=============THE END==============')

