#!/usr/local/bin/python

#from thomas import AddrBookEntry
#from thomas import EmpAddrBookEntry

#from thomas import say_hello as sh
from sys import path

#import packet.orange as ora

#from packet.orange import *
from time import ctime, sleep

def tsfunc(func):
    def wrappedFunc():
        print '[%s] %s() called' % (ctime(), func.__name__)
        return func()
    return wrappedFunc

@tsfunc
def foo():
    pass

def show_path():
    for each in path:
        print each



def main():
    print 'orange age %d' % orange_age
    #print 'car number is ', _car_number
    name()

def fun():
    sum = 0
    for i in range(1000):
        sum += i;
    return sum

def h():
    print 'Wen Chuan',  
    m = yield 5 # Fighting!  
    print m  
    d = yield 12  
    print 'We are together!'  
    c = h()
    m = c.next()
    d = c.send('Fighting!')
    print 'We will never forget the date', c, '.', d

    
import cProfile
import pstats
    
if __name__=='__main__':
    #cProfile.run("fun()", "fun_profile")
    
    #p = pstats.Stats("prof.txt")
    #p.sort_stats("time").print_stats()

    h()
	
