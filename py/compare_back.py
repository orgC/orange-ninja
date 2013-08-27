#!/usr/local/bin/python

import os
import sys
import types
import re
import datetime
import getopt

from ats_utils import ats_log as log

sys.path.append('/root/work/rts/rts_django')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rts_django.settings")
from db.models import offical_load, rts_case, src_file, line_executed

from config import compare_config as ccfg

#svn_diff_path='../svn_diff_log'

class diff_section(object):
    def __init__(self, section):
        #self.name    = name
        self.section = section
        self.old_no_list = []
        self.new_no_list = []
        self.cur_old_no = 1
        self.cur_new_no = 1

    def check_code_valid(self):
        pass

    def print_modified_no(self):
        print '===================================='
        print ' %s ' % self.file_name
        print '===================================='

        i=0
        for line in self.old_no_list:
            i += 1
            print '\t-%d  ' % line, 
            if i % 5 == 0:
                print ' '
            

    def print_info(self):
        print '===================================='
        print ' %s ' % self.file_name
        print '===================================='
        
        for line in self.old_no_list:
            print '\t-%d' % line
            
        for line in self.new_no_list:
            print '\t+%d' % line

    def parse_section(self):
        try:
            for line in self.section.split('\n'):
                #get the source file name
                if line[0:7] == 'Index: ':
                    m = re.match(r'Index: (?P<name>.*)$', line)
                    if m:
                        self.file_name = m.group('name')
                    else:
                        log("get source file failed")

                elif line[0:5] == '=====':
                    pass

                #get version
                elif line[0:3] == '---':
                    m = re.match(r'[^(]*([^)]*)', line)
                    if m:
                        self.version = m.group(1)[1:]
                    else:
                        log("get version failed")
                        
                elif line[0:3] == '+++':
                    pass
                    
                elif line[0:2] == '@@':
                    m = re.match(r'@@ (?P<f>.*) @@', line)
                    if m:
                        #print m.group('f')
                        src_line = m.group('f')
                        old_tmp, new_tmp = m.group('f').split()
                        try:
                            old_no, old_line = old_tmp[1:].split(',')
                            new_no, new_line = new_tmp[1:].split(',')
                            #self.old_line = int(old_line)
                            #self.new_line = int(new_line)
                        except ValueError, e:
                            #log("This is a special ")
                            old_no = old_tmp[1:]
                            new_no = new_tmp[1:]
                            #self.old_line = 0
                            #self.new_line = 0

                        self.cur_old_no = int(old_no) - 1
                        self.cur_new_no = int(new_no) - 1
                    
                elif line[0] in (' ', '-', '+'):
                    if line[0] == ' ':
                        self.cur_old_no += 1
                        self.cur_new_no += 1

                    elif line[0] == '-':
                        self.cur_old_no += 1
                        self.old_no_list.append(self.cur_old_no)

                    elif line[0] == '+':
                        self.cur_new_no += 1
                        self.new_no_list.append(self.cur_new_no)

                    else:
                        print 'May be some error occurent (inner) ... '
                else:
                    log(line)
                    print 'May be some error occurent (outer) ... '

        except IndexError, result:
            #log("This section is finished. return ")
            pass
            
def svn_diff(branch1, branch2):
    '''svn diff, got the diff file '''
    diff1 = os.path.basename(branch1)
    diff2 = os.path.basename(branch2)
    diff1 = diff1.replace('-', '.')
    diff2 = diff2.replace('-', '.')

    #print '%s  %s' % (diff1, diff2)
    
    diff_file = '%s-%s.diff' % (diff1, diff2)
    #print '%s' % diff_file 
    svn_cmd = 'svn diff %s %s > %s/%s' % (branch1, branch2, ccfg['svn_diff_path'], diff_file)
    print 'svn diff %s %s > %s/%s' % (branch1, branch2, ccfg['svn_diff_path'], diff_file)
    os.system(svn_cmd)
    
    return diff_file

def split_section(diff_file):

    g_list = []
    
    with open('%s' % (diff_file)) as fd:
        sec_list = []
        for line in fd:
            m = re.match(r'^Index:', line)
            if m:
                if len(sec_list) > 0:
                    string = ''.join(sec_list)
                    g_list.append(string)
                    
                sec_list = []
                print '%s' % line.strip('\n')
                sec_list.append(line)
            else:
                sec_list.append(line)
        string = ''.join(sec_list)
        g_list.append(string)
        #print string
    return g_list
    #print list content

class file_info(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.line_list = []

    def add_line_no(self, line_no):
        self.line_list.append(line_no)

    def get_line_list(self):
        return self.line_list

    def get_file_name(self):
        return self.file_name

    def file_line_count(self):
        return len(self.line_list)
        

class case_info(object):
    def __init__(self, load_name, case_id):
        self.load_name = load_name
        self.case_id = case_id
        self.file_list = []
        self.select_flag = False

    def check_selected(self):
        return self.select_flag

    def get_case_id(self):
        return self.case_id

    def add_src_file(self, f_info):
        self.file_list.append(f_info)
        self.select_flag = True

    def print_info(self):
        print '%s' % self.case_id
        for buf in self.file_list:
            print "            %s: " % buf.get_file_name(), 
            for line in buf.get_line_list():
                print "%d  " % line, 
            print ' '
        
    def log_info(self, fp):
        fp.write('%-20s  %-15s\n' % (self.load_name, self.case_id))
        
        for file_buf in self.file_list:
            fp.write("    %s: " % file_buf.get_file_name())
            for line in file_buf.get_line_list():
                fp.write("%d  " % line)
            fp.write("\n")
        fp.write('\n')

def compare_with_base(load_name, diff_list):

    log("compare %s" % load_name)
    #need try ... cache block 
    db_load = offical_load.objects.get(ats_load_name = load_name)

    case_list = rts_case.objects.filter(ats_load_fk = db_load.id)
    
    choiced_case_list = []
    stat_info_list = []
    log("start compare ... ")
    for each_case in case_list:
        case_select_flag = False
        case_buf = case_info(load_name, each_case.ats_case_id)
        stat_info_list.append(case_buf)
        
        for each_diff in diff_list:
            if case_select_flag:
                pass
                #log("This case has been slelected ... ", color='red')
                #break
            
            #log("caseid = %d, src_name = %s" % (each_case.id, os.path.basename(each_diff.file_name)))
            db_src_list = src_file.objects.filter(ats_case_fk = each_case.id, \
                            ats_src_name = os.path.basename(each_diff.file_name))
            if len(db_src_list) != 1:
                continue
                
            db_src = db_src_list[0]
            file_buf = file_info(db_src.ats_src_name)
            #stat_info_list.append(st_info)
            for each_diff_line in each_diff.old_no_list:
                
                db_line_list = line_executed.objects.filter(ats_src_file_fk = db_src.id, \
                                ats_line_num = each_diff_line)
                if len(db_line_list) == 1:
                    #log("srcid = %d, line number = %d" % (db_src.id, each_diff_line), color='red')
                    db_line = db_line_list[0]
                    choiced_case_list.append(each_case.id)
                    case_select_flag = True
                    file_buf.add_line_no(db_line.ats_line_num)
                    
                    #log("matched load %s case %s file %s line %d modified !" % \
                    #    (db_line.ats_load_name, db_line.ats_case_id, db_src.ats_src_name, db_line.ats_line_num), color='white') 
                    #break
                else:
                    pass
            if file_buf.file_line_count() > 0:
                #case_buf.get_file_list().append(file_buf)
                case_buf.add_src_file(file_buf)

    log("end compare ... ")
    return stat_info_list

def usage():
    print 'Usage: compare '
    print '  -l, --load %-30s' % 'load_name'
    print '  -d, --diff %-30s' % 'diff_file'
    print '  -o, --old  %-30s' % 'old_branch'
    print '  -n, --new  %-30s' % 'new_branch'
    
    sys.exit(1)
    
def main(argv):

    diff_file = ''
    load_name = ''
    old_branch = ''
    new_branch = ''

    try: 
        opts, args = getopt.getopt(argv, "hl:d:o:n:", ["help", "load=", "diff=", "old=", "new="])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(1)
        elif opt in ("-l", "--load"):
            load_name = arg
        elif opt in ("-d", "--diff"):
            diff_file = arg
        elif opt in ("-o", "--old"):
            old_branch = arg
        elif opt in ("-n", "--new"):
            new_branch = arg

    if load_name:
        pass
    else:
        print 'no load_name'
        usage()

    if diff_file:
        print 'diff file %s' % diff_file
        pass
    else:
        if old_branch and new_branch:
            diff_file = diff_file = svn_diff(old_branch, new_branch)
        else:
            print 'no old branch or new branch '
            usage()
        
    g_list = split_section("%s/%s" % (ccfg['svn_diff_path'], diff_file))
    ds_list = []
    
    for item in g_list:
        ds = diff_section(item)
        ds.parse_section()
        #ds.print_info()
        ds_list.append(ds)

    com_list = compare_with_base(load_name, ds_list)
    fp = open("%s/%s-%s.out" %  \
        (ccfg['compare_result'], diff_file, datetime.datetime.now().strftime('%m%d-%H%M%S')), 'w')

    print 'case number: %d' % len(com_list)
    length = 0
    result_list = []
    for each in com_list:
        if each.check_selected():
            length += 1
            result_list.append(each.get_case_id())
            each.log_info(fp)
            each.print_info()

    print 'selected case number %d' % length
    for each_case in result_list:
        print '    %s' % each_case

    fp.close()
    
if __name__ == '__main__':
    if len(sys.argv) == 0:
        print 'argv == 0'
        usage()
        
    main(sys.argv[1:])
    
    

    
    

