#!/usr/bin/env python

import datetime
import sys

def ats_log(str_trace, color='green'):
    dict_color = {'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'white': 37}
    if color in dict_color.keys():
        cv = dict_color[color]
        print "\033[%dm%s%20s:%03d %s\033[0m" %(cv, datetime.datetime.now().strftime('%m%d-%H:%M:%S'),
                sys._getframe().f_back.f_code.co_name,
                sys._getframe().f_back.f_lineno, 
                str_trace);

def ats_log_log(str_stace, out = sys.stdout):
    pass
    
    
