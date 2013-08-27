#!/usr/local/bin/python

import sys
import os
import re
import types
import commands
import time
import getopt
import MySQLdb as mdb

sys.path.append('/root/work/rts/rts_django')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rts_django.settings")

from db.models import offical_load, rts_case, src_file, line_executed
from ats_utils import ats_log as log
from config import read_config as rcfg
from config import common_config as ccfg

class gcov_info(object):
    def __init__(self, load_info, case_info, file_name, db_con):
        self._file_name = file_name
        self.data = {}
        self._load_info = load_info
        self._case_info = case_info
        self.conn = db_con
        self.cur = self.conn.cursor()
        self.src_name, ext = os.path.splitext(os.path.basename(file_name))
        
    def parse_gcov_log(self):
        self.fp = open(self._file_name)
        for each_line in self.fp:
            str_line_list = each_line.split(':')
            try:
                ret = int(str_line_list[0])
                self.data[str_line_list[1].strip()] = str_line_list[0].strip()
            except:
                pass
        #save the source file name without load path
        p = re.compile(r'^%s/' % rcfg['prj_root'])
        self._src_file_name = p.sub('', self._file_name)
        
        #p = re.compile(r'.gcov$')
        #self._src_file_name = p.sub('', tmp_file_name)

    def show_dict(self):
        if len(self.data) == 0:
            return
        print '============== %s ==============' % (self._file_name)
        for key in self.data:
            print '%s : %s' % (key, self.data[key])

    def save(self):        
        self.cur.execute("insert into db_src_file \
                    (ats_case_fk_id, ats_load_name, ats_case_id, ats_path_name, ats_src_name, ats_timestamp) \
                    value(%d, '%s', '%s', '%s', '%s', now())" % \
                    (self._case_info.id, self._load_info.ats_load_name, \
                    self._case_info.ats_case_id, self._src_file_name,\
                    self.src_name))

        count = self.cur.execute("select id from db_src_file where ats_case_fk_id = %d and ats_path_name = '%s' LIMIT 1" % \
                                    (self._case_info.id, self._src_file_name))

        if count == 1:
            src_file_id = self.cur.fetchone()
        else:
            log("fetch src file id failed, insert failed")
            return
        
        for key in self.data:
        
            self.cur.execute("insert into db_line_executed(ats_src_file_fk_id, ats_load_name, \
                                ats_case_id, ats_path_name, ats_line_num, ats_exec_count, ats_timestamp) \
                                value(%d, '%s', '%s', '%s', %d, %d, now())" % \
                                (src_file_id[0], self._load_info.ats_load_name,\
                                self._case_info.ats_case_id, self._src_file_name, \
                                int(key),\
                                int(self.data[key])))
        
        '''
        if len(self.data) == 0:
            return
        src_file_info = src_file(ats_case_fk   = self._case_info, \
                                 ats_load_name = self._load_info.ats_load_name, \
                                 ats_case_id   = self._case_info.ats_case_id, \
                                 ats_path_name = self._file_name, \
                                 ats_src_name  = self.src_name)
        src_file_info.save()
        
        for key in self.data:
            line_exec_info = line_executed( ats_src_file_fk = src_file_info, \
                                            ats_load_name   = self._load_info.ats_load_name, \
                                            ats_case_id     = self._case_info.ats_case_id, \
                                            ats_path_name   = self._file_name, \
                                            ats_line_num    = int(key), \
                                            ats_exec_count  = int(self.data[key]))

            line_exec_info.save()
        '''     

def clean_foot(path):
    log("clean foot at %s" % path)

    if os.path.exists(path):
        pass
    else:
        print '%s is not exist' % path
        return

    gcov_num = commands.getoutput("find %s -name '*.gcov' | wc -l" % path)
    gcda_num = commands.getoutput("find %s -name '*.gcda' | wc -l" % path)
    log('gcov files number %s, gcda files number %s' % (gcov_num.strip('\n'), gcda_num.strip('\n')))
    #time.sleep(3)
    os.system("find %s -name '*.gcov' -o -name '*.gcda' | xargs rm " % path);

# login the specific machine. 

def flush_gcda_to_gcov(path):
    if os.path.exists(path):
        pass
    else:
        print '%s is not exist' % path
        return
    
    for root, dirs, files in os.walk(path):
        if '.svn' in dirs:
            dirs.remove('.svn')
        
        for each_file in files:
            m = re.search(".*\.gcda$", each_file)
            if m:
                #print 'current dir is %s  ---> %s' % (root, each_file)
                os.chdir(root)
                commands.getoutput('gcov *.gcda')
                break
            else:
                continue
            
        for each_dir in dirs:
            local_root = "%s/%s" % (root, each_dir)
            dirs.remove(each_dir)
            flush_gcda_to_gcov(local_root)


def db_connect_init(db_addr, user, passwd, db_name):
    try:
        con = mdb.connect(db_addr, user, passwd, db_name);
        cur = con.cursor()
        return cur
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

def exec_sql_command(cur, msg, auto_commit=True, debug=0):
    try:
        if(debug==1):
            print msg
        cur.execute(msg)
        if auto_commit:
            cur.execute('commit')
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])

def fetch_data_from_db(cur, sql_cmd, debug=0):
    if debug==1:
        print sql_cmd
    cur.execute(sql_cmd)
    return cur.fetchall()

def flush_gcda_files_from_specific_dir(path, *specific_dirs):
    spec_dir_array = []

    gcov_num = commands.getoutput("find %s -name '*.gcov' | wc -l" % path)
    gcda_num = commands.getoutput("find %s -name '*.gcda' | wc -l" % path)
    log('flush gcda files\n\tgcov files number %s, gcda files number %s' % (gcov_num.strip('\n'), gcda_num.strip('\n')))
    
    for each_xarg in specific_dirs:
        spec_dir_array.append(each_xarg)

    if len(spec_dir_array) != 0:
        for each_spec_dir in spec_dir_array:
            flush_gcda_to_gcov(path + '/' + each_spec_dir)

    else:
        print 'No specific directory. visit all directory'
        for root, dirs, files in os.walk(path):
            if '.svn' in dirs:
                dirs.remove('.svn')
            for each_dir in dirs:
                flush_gcda_to_gcov('%s/%s' % (root, each_dir))

def parse_gcov_file2(load_info, case_info, file, db_conn):

    #print "parse %s" % file
    a = gcov_info(load_info, case_info, file, db_conn)
    a.parse_gcov_log()
    #a.show_dict()
    a.save()
    
 
def parse_gcov_file(load_info, case_info, path, db_conn):

    gcov_list = []
    
    for root, dirs, files in os.walk(path):
        if '.svn' in dirs:
            dirs.remove('.svn')
        
        for each_file in files:
            m = re.search(".*\.gcov$", each_file)
            if m:
                #parse_gcov_file2(load_info, case_info, '%s/%s' % (root, each_file), db_conn)
                gcov_list.append(each_file)
            else:
                continue
        
        for each_dir in dirs:
            dirs.remove(each_dir)
            parse_gcov_file(load_info, case_info, '%s/%s' % (root, each_dir), db_conn)

    print '\n================================================='
    for each_item in gcov_list:
        print each_item
    print '\n================================================='

def add_action(db_conn, prj_path, prj_src_path_tail, log_path):
    #load_info = offical_load(ats_load_name = load_name)
    #load_info.save()
    #os.system('rm -rf %s/%s' % (log_path, prj_name))
    for gcda_log_dir in os.listdir(log_path):
        result = re.search(r"finished", gcda_log_dir)
        if result:
            print ' %s has been processed. skip it' % gcda_log_dir
            continue

        name_backup = gcda_log_dir
        load_id, case_id, time_stamp = gcda_log_dir.split('__')

        load_list = offical_load.objects.filter(ats_load_name=load_id)
        if len(load_list) == 1:
            load_info = load_list[0]
        else:
            load_info = offical_load(ats_load_name = load_id)
            load_info.save()
        
        case_info = rts_case(ats_case_id=case_id, ats_load_name=load_info.ats_load_name, \
                    ats_load_fk=load_info)
        case_info.save()

        log('mv %s/%s %s/%s' % (log_path, gcda_log_dir, log_path, load_id))
        os.rename('%s/%s' % (log_path, gcda_log_dir), '%s/%s' % (log_path, load_id))
        log('cp -rfp %s/%s %s' % (log_path, load_id, prj_path))
        os.system('cp -rfp %s/%s %s' % (log_path, load_id, prj_path))

        prj_src_dir = '%s/%s/%s' % (prj_path, load_id, prj_src_path_tail)
        print 'project src path %s' % prj_src_dir

        #flush_gcda_files_from_specific_dir(prj_src_dir, 'application', 'XuanWu')
        flush_gcda_files_from_specific_dir(prj_src_dir)
        #gcov process 
        parse_gcov_file(load_info, case_info, prj_src_dir, db_conn)
        clean_foot(prj_src_dir)
        os.rename('%s/%s' % (log_path, load_id),  '%s/%s.finished' % (log_path, name_backup))

def del_action(argv):
    load_name = ''
    case_name = ''

    try:
        opts, args = getopt.getopt(argv, "hl:c:", ["help", "load=", 'case='])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(1)
        elif opt in ("-l", "--load"):
            load_name = arg
        elif opt in ("-c", "--case"):
            case_name = arg

    if load_name:
        if case_name:
            print "delete load %s, case %s" % (load_name, case_name)
            
            case_info = rts_case.objects.filter(ats_case_id=case_name, ats_load_name=load_name)
            case_info.delete()
        else:
            print "case_name is empty, delete load %s" % load_name
            load_info = offical_load.objects.filter(ats_load_name=load_name)
            load_info.delete()
    else:
        print 'There are no load name'
        usage()
        pass
    
    #load_info = offical_load.objects.filter(ats_load_name=load_name)
    #rts_info  = rts_case.objects.filter() 
    
def usage():
    print 'Usage: read.py add|del [load_name]'

def db_init(host, user, password, port=3306):
    try:
        conn = mdb.connect(host=host, user = user, passwd = password, port=port)
        conn.select_db('rts_db')
        return conn
    except mdb.Error, e:
        log("connect db(User: %s Password: %s Host: %s Port: %d) failed" % \
            (user, password, host, port))
        return None

def main():
    db_conn = db_init(rcfg['db_host'], rcfg['db_user'], rcfg['db_password'], rcfg['db_port'])
    if db_conn == None:
        log('connect to db failed, exit ...')
        return
    else:
        pass

    add_action(db_conn, rcfg['prj_root'], rcfg['prj_src_tail'], rcfg['gcov_path'])

    db_conn.commit()
    db_conn.close()
    '''        
    elif command == 'del':
        if len(argv) > 1:
            del_action(argv[1:])
        else:
            usage()
            log("usage 2")
            sys.exit(1)
    else:
        usage()
        log("usage 3")
        sys.exit(1)
    '''        
if __name__ == '__main__':
    import cProfile
    import pstats

    '''
    while True:
        main()
        time.sleep(5)
        print 'sleep 5 seconds'

    '''
    cProfile.run("main()", filename="prof.txt")
    p = pstats.Stats("prof.txt")
    p.sort_stats("time").print_stats(30)


