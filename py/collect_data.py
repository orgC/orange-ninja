#!/usr/bin/python
# Filename: collect_data.py
# debian  apt-get install python-pexpect 
import os, sys, time, re
from neo_common import log_info
from neo_common import ssh_connection

def print_help_info():
    print('''    Diagnosis data Collector v01, 2013-04-02 [EZC Software Development Team]
        %s <slot-number, 3~14> <application-type, hsgw, pdsn> [unstable]
    Example:
        %s 10 hsgw
        %s 10 hsgw unstable  # the application will be restarted.
        %s 10 pdsn
        %s 10 haccg''' %(sys.argv[0],sys.argv[0],sys.argv[0],sys.argv[0],sys.argv[0]))
    sys.exit()

class ssh_on_slotx(ssh_connection):
    def __init__(self, slot_num, str_app_type,base_name,repo_path):
        self.str_app_type = str_app_type
        self.int_slot=slot_num
        self.base_name=base_name
        self.repo_path=repo_path
        if 0 != os.system('mkdir '+self.repo_path):
            log_info('Failed! mkdir '+self.repo_path)
        self.log_file_name='%s/slot_cmd_output.log' %self.repo_path
        super(ssh_on_slotx,self).__init__('slot-%d' %slot_num,'root','pdg.net')
        #super(ssh_on_slotx,self).__init__('127.0.0.1','root','pdg.net')

    def login_CLI(self):
        self.set_prompt('system# ')
        self.send_command('su - sysadmin', timeout=10)
        #self.send_command('cli', timeout=10)
        self.clean_buff()
        if self.str_app_type == 'system':
            log_info('login CLI type=system')
            return
        self.set_prompt(self.str_app_type+'# ')
        self.send_command('set context=%s' %self.str_app_type,timeout=5)
        self.clean_buff()
        self.send_command('cls',timeout=10)
        log_info('login CLI type='+self.str_app_type)

    def logout_CLI(self):
        self.set_prompt('tmp# ')
        self.send_command('exit')
        self.clean_buff()
        log_info('logout CLI type='+self.str_app_type)

    def __enter_ma_shell(self):
        self.set_prompt('MA\$')
        self.send_command('attach where=ma\n', timeout=5)
        self.clean_buff()
        self.send_command('exit')
        log_info('enter_ma_shell type='+self.str_app_type)

    def __enter_app_shell(self):
        self.set_prompt('% ')
        self.send_command('attach where='+self.str_app_type, 5)
        self.clean_buff()
        self.send_command('exit')
        self.set_prompt('WinG% ')
        log_info('enter_app_shell type='+self.str_app_type)

    def __leave_x_shell(self):
        self.set_prompt(self.str_app_type+'# ')
        self.send_command('\3\n', timeout=2)
        self.clean_buff()
        log_info('leave_x_shell type='+self.str_app_type)

    def __write_log_file(self,str_content):
        try:
            file_object = open(self.log_file_name, 'a')
        except:
            log_info("Failed! open %s 'a'" %self.log_file_name)
            return
        try:
            file_object.write(time.strftime('\n================== %Y%m%d-%H:%M:%S =================\n',time.localtime(time.time())))
            file_object.write(str_content)
        except:
            log_info("Failed! write %s" %self.log_file_name)
        file_object.close()

    def __proc_multi_line_cmd(self,command_block):
        cmd_list = re.split('[\r\n]+\s*', command_block)
        for command in cmd_list:
            match_sleep = re.search('sleep\s+(\d+)', command)
            if match_sleep:
                try:
                    duration = eval(match_sleep.group(1))
                    time.sleep(duration)
                except:
                    log_info("Failed! exec %s" %command)
            elif re.search('[\w\d]+', command):
                log_buff=self.send_command(command, timeout=30)
                self.__write_log_file(log_buff)
                self.clean_buff()

    def exec_ma_commands(self,command_block):
        if self.str_prompt == 'tmp# ':
            self.login_CLI()
        self.__enter_ma_shell()
        self.__proc_multi_line_cmd(command_block)
        self.__leave_x_shell()

    def exec_app_commands(self,command_block):
        if self.str_prompt == 'tmp# ':
            self.login_CLI()
        self.__enter_app_shell()
        self.__proc_multi_line_cmd(command_block)
        self.__leave_x_shell()

    def exec_cli_commands(self,command_block):
        if self.str_prompt == 'tmp# ':
            self.login_CLI()
        self.__proc_multi_line_cmd(command_block)

    def exec_linux_commands(self,command_block):
        if self.str_prompt != 'tmp# ':
            self.logout_CLI()
        self.__proc_multi_line_cmd(command_block)
        
    def parse_dmp_files(self):
        if self.str_prompt != 'tmp# ':
            self.logout_CLI()
        self.send_command('gensym.sh /opt/utsnt/sbin/%s' %self.str_app_type, timeout=30)
        log_buff=self.send_command('ls -ltr /opt/utsnt/run/*.dmp /tmp/*.dmp --color=never', timeout=30)
        self.__write_log_file(log_buff)
        #-rw------- 1 root root 250040 2013-03-20 20:18 /opt/utsnt/run/1a20db4b-4b99-33df-4c468505-7e19f132.dmp
        #-rw------- 1 root root 223048 2013-04-02 11:23 /tmp/074f1049-b3f1-9306-6f080521-346077f3.dmp
        for dump_file in re.findall('\d\d:\d\d\s+([a-z\d\/\-]+\.dmp)',log_buff):
            try:
                log_buff=self.send_command('viewlog.sh '+dump_file, timeout=30)
                self.__write_log_file(log_buff)
            except:
                pass

def collect_info_on_hsgw(int_slot_num,base_name,repo_path):
    try:
        ssh2slot=ssh_on_slotx(int_slot_num, 'hsgw',base_name,repo_path)
    except:
        log_info("ssh slot-%s failed." %int_slot_num)
        return
    ma_commands='''
        print_mp
        print_sa'''
    app_commands='''
        CpuUsage
        dr
        PI Listpi
        sleep 5
        PI Listpi
        sleep 5
        PI Listpi
        sleep 5
        PI Listpi
        sleep 5
        PI Listpi
        sleep 5
        PI Listpi
        sleep 5
        PI Listpi
        sleep 5
        PI Listpi
        sleep 5
        PI Listpi
        sleep 5
        PI Listpi
        listpools
        dp
        lt
        lm
        Sa ListSaInfo
        ui dq
        rp ShowLastErr 10000
        rp scs
        rp ShowMsgStats
        rp ShowNcepsStat
        ppp ss
        ppp ShowMessgeStats
        ppp ShowPrepaidStats
        sc ShowStats'''
    cli_commands='''
        show active-session summary
        show vr throughput
        show ppp statistics
        show rp reg-req
        show call-statistics statistics
        show aaa di-server'''
    linux_commands='''
        top -b -n 8
        mpstat -P ALL 2 8'''
    minidump_cmds='''
        genminidump.sh hsgw
        sleep 2
        genminidump.sh hsgw
        sleep 2
        genminidump.sh hsgw
        sleep 2
        genminidump.sh hsgw
        sleep 2
        genminidump.sh hsgw
        sleep 2
        genminidump.sh hsgw
        sleep 2
        genminidump.sh hsgw
        sleep 2
        genminidump.sh hsgw
        sleep 2
        genminidump.sh hsgw
        sleep 2
        genminidump.sh hsgw
        sleep 2
        scp /tmp/*.dmp 197.1.20.3:%s
        scp /opt/utsnt/run/*.dmp 197.1.20.3:%s
        scp /opt/utsnt/run/*.crashdump 197.1.20.3:%s
        ''' %(repo_path, repo_path, repo_path)

    ssh2slot.exec_ma_commands(ma_commands)
    ssh2slot.exec_app_commands(app_commands)
    ssh2slot.exec_cli_commands(cli_commands)
    ssh2slot.exec_linux_commands(linux_commands)
    try:
        type(sys.argv[3])
        if 'unstable' == sys.argv[3]:
            ssh2slot.exec_linux_commands(minidump_cmds)
    except:
        pass
    ssh2slot.parse_dmp_files()
    try:
        type(sys.argv[3])
    except:
        log_info('collect_info_on_hsgw finished.')
        return
    if 'unstable' == sys.argv[3]:
        start_app_cmds='''
            /etc/init.d/monit stop
            /etc/init.d/hsgw  stop
            /opt/utsnt/sbin/hsgw'''
        ssh2slot.exec_linux_commands(start_app_cmds)
        ssh2slot.ssh_handle.send('\3')
        ssh2slot.send_command('y', timeout=2)
        ssh2slot.clean_buff()
        start_app_cmds='''
            /etc/init.d/monit start
            /etc/init.d/monit start'''
        ssh2slot.exec_linux_commands(start_app_cmds)
        log_info('restart app finished.')

def collect_info_on_sysmgr(slot_num,base_name,repo_path):
    '''if 0 != os.system   ('scp slot-%d:/opt/utsnt/run/*.dmp %s' %(slot_num,repo_path)):
        log_info('Failed! scp slot-%d:/opt/utsnt/run/*.dmp %s' %(slot_num,repo_path))
    if 0 != os.system   ('scp slot-%d:/opt/utsnt/run/*.crashdump.* %s' %(slot_num,repo_path)):
        log_info('Failed! scp slot-%d:/opt/utsnt/run/*.crashdump.* %s' %(slot_num,repo_path))
    if 0 != os.system   ('scp slot-%d:/tmp/*.dmp %s' %(slot_num,repo_path)):
        log_info('Failed! scp slot-%d:/tmp/*.dmp %s' %(slot_num,repo_path))'''
    if 0 != os.system   ('cp /home/ftp/neconfig/slot-%d/*.dmp %s' %(slot_num,repo_path)):
        log_info('Failed! cp /home/ftp/neconfig/slot-%d/*.dmp %s' %(slot_num,repo_path))
    if 0 != os.system   ('cp /var/log/tmp/slot%d.app.log* %s' %(slot_num,repo_path)):
        log_info('Failed! cp /var/log/tmp/slot%d.app.log* %s' %(slot_num,repo_path))
    if 0 != os.system   ('cp /var/log/tmp/slot%d.ma.log* %s' %(slot_num,repo_path)):
        log_info('Failed! cp /var/log/tmp/slot%d.ma.log* %s' %(slot_num,repo_path))
    if 0 != os.system   ('cp /var/log/tmp/slot%d.monit.log* %s' %(slot_num,repo_path)):
        log_info('Failed! cp /var/log/tmp/slot%d.monit.log* %s' %(slot_num,repo_path))
    if 0 != os.system   ('cp /var/log/tmp/slot%d.sys.log* %s' %(slot_num,repo_path)):
        log_info('Failed! cp /var/log/tmp/slot%d.sys.log* %s' %(slot_num,repo_path))
    if 0 != os.system('tar -czf /home/%s.tar.gz %s' %(base_name,repo_path)):
        log_info('Failed! tar -cvf /home/%s.tar %s' %(base_name,repo_path))

def main_process():
    int_slot_num=0
    try:
        int_slot_num = eval(sys.argv[1])
    except:
        print_help_info()
    if int_slot_num>14 or int_slot_num<3:
        print_help_info()
    try:
        type(sys.argv[2])
    except:
        print_help_info()
    try:
        type(sys.argv[3])
        if 'unstable' != sys.argv[3]:
            print_help_info()
    except:
        pass
    base_name='diagnosis_slot%d_%s' %(int_slot_num,time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time())))
    repo_path='/tmp/'+base_name
    if sys.argv[2]=='hsgw':
        collect_info_on_hsgw(int_slot_num,base_name,repo_path)
        collect_info_on_sysmgr(int_slot_num,base_name,repo_path)
    else:
        log_info('Unkown application type.')

if __name__=='__main__':
    log_info('============= START ==============')
    main_process()
    log_info('=============THE END==============')