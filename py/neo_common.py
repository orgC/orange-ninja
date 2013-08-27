#!/usr/bin/python
# Filename: collect_data.py
# debian  apt-get install python-pexpect 
import os, sys, datetime, re
import pexpect

def log_info(str_trace):
    print "\033[32m%s%20s:%03d %s\033[0m" %(datetime.datetime.now().strftime('%m%d-%H:%M:%S'),
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
                'yes/no',                                # 0  If added new line here, please notice
                'password',                              # 1  the index is used in the if elif lines.
                 '#',                                    # 2
                'Permission denied, please try again.',  # 3
                pexpect.TIMEOUT,                         # 4
                'Connection closed by UNKNOWN',          # 5
                pexpect.EOF], timeout=6)                 # 6
            if   0 == exp_index:
                self.ssh_handle.sendline('yes')
            elif 1 == exp_index:
                self.ssh_handle.sendline(password)
            elif 2 == exp_index:
                if 1==debug_on:
                    self.ssh_handle.logfile=sys.stdout
                self.clean_buff()
                self.set_prompt('tmp# ')
                self.send_command('cd /tmp',timeout=5)
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

