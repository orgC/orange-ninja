#!/usr/local/bin/python

import sys, os, re, types, commands, time
import threading

def flush_command(path):
    os.chdir(path)
    #print "current path %s" % os.getcwd()
    #print 'run command:  gcov *.gcda'
    #os.system("gcov -n *.gcda")
    result = commands.getoutput('gcov *.gcda')
    #print result

def endwith(s, *endstring):
    array = map(s.endswith, endstring)
    if True in array:
        return True
    else:
        return False    

def flush_gcda_to_gcov(path):
    if os.path.exists(path):
        pass
    else:
        print '%s is not exist' % path
        return
    #fd = open("gcov.log", 'w')

    threads = []
    nloop = 0
    
    for root, dirs, files in os.walk(path):
        for each_file in files:
            m = re.search(".*\.gcda$", each_file)
            if m:
                os.chdir(root)
                #result = commands.getoutput('gcov -n *.gcda')
                #fd.write(result)
                #os.system('gcov *.gcda')
                #print '=======>>', root
                t = threading.Thread(target=flush_command, args=(root, ))
                threads.append(t)
                nloop = nloop+1
                break
            else:
                continue

    nloops = range(nloop)
    for i in nloops:
        threads[i].start()

    for i in nloops:
        threads[i].join()

    #fd.close()

def flush_gcov_one_by_one(path):
    os.chdir(path)
    for filename in os.listdir(path):
        if filename.endswith('gcda'):
            result = commands.getoutput('gcov %s' % filename)



def check_tail(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if endwith(f, 'gcno', 'gcda'):
                pass
            else:
                print f


def check_mismatch(path):

    mismatch = 0
    matched  = 0
    fp = open('mismatch.log', 'w')

    for root, dirs, files in os.walk(path):
        
        for f in files:
            os.chdir(root)
            if endwith(f, 'gcda'):
                command = '''hexdump -e '"%x"' -s8 -n4 '''
                da_result = commands.getoutput(command + f)
                #print da_result
                f_no = f.replace('gcda', 'gcno')
                #print f_no
                no_result = commands.getoutput(command + f_no)
                if da_result != no_result:
                    mismatch = mismatch+1
                    fp.write("%s: %s\n" % (f, da_result))
                    fp.write("%s: %s\n\n" % (f_no, no_result))
                else:
                    matched = matched+1
                    print "%s: %s\n" % (f, da_result)
                    print "%s: %s\n" % (f_no, no_result)

    print "mismatch number is %d" % mismatch
    print "matched number is %d" % matched
    
    fp.close()

def print_thread(path, no, *files):
    #from sys.stdout import write as printf
    
    print '\n######%s__%d' % (path, no)
    for each in files[0]:
        print each

def print_walk_path(path):
    from os.path import join, isdir

    nloop = 0
    threads = []

    for root, dirs, files in os.walk(path):
        if files:
            nloop = nloop + 1
            #t = threading.Thread(target=print_thread, args=(root, nloop, files))
            t = threading.Thread(target=flush_command, args=(root, ))
            threads.append(t)
            '''
            for each_dir in dirs:
                #local_root = "%s/%s" % (root, each_dir)
                local_root = join(root, each_dir)
                #dirs.remove(each_dir)
                print '%s' % local_root
                #print_walk_path(local_root)
                nloop = nloop + 1
'''
    nloops = range(nloop)
    for i in nloops:
        threads[i].start()

    for i in nloops:
        threads[i].join()

    print nloop


#def mywalk1(top, topdown=True, onerror=None, followlinks=False):
def mywalk1(top):
    print 'Enter mywalk'
    from os.path import join, isdir, islink

    count = 0;

    try:
        # Note that listdir and error are globals in this module due
        # to earlier import-*. 
        names = listdir(top)
        print names
    except error, err:
        if onerror is not None:
            onerror(err)
        return

    dirs, nondirs = [], []
    for name in names:
        if isdir(join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
  
    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        path = join(top, name)
        if followlinks or not islink(path):
            for x in mywalk(path, topdown, onerror, followlinks):
                yield x
    if not topdown:
        yield top, dirs, nondirs


def main():
    print_walk_path("/opt/gcov_log_819/EPG__10006__1373974766.6.finished")
    #mywalk1("/opt/gcov_log_819/EPG__10006__1373974766.6.finished")
    
if __name__ == '__main__':
    #flush_gcda_to_gcov("/root/HSGW-2.0")
    import cProfile
    import pstats
    import datetime

    print datetime.datetime.now()
    main()
    print datetime.datetime.now()
    
    
    '''
    cProfile.run("main()", filename="prof.txt")
    p = pstats.Stats("prof.txt")
    p.sort_stats("time").print_stats(30)    
    '''
