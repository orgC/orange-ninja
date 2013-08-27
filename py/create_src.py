#!/usr/bin/env python
import sys
sys.setrecursionlimit(1000000)

def init_file(src_name):
    try:
        fp = open(src_name, 'w')
        return fp
    except:
        print 'open %s failed' % src_name
        return None

def create_foo(fp, pre_str, max_no, no=0, final_flag=False):
    if no > max_no:
        print 'reach the max no, break'
        return None
        
    if not no:
        fp.write("#include<stdio.h>\n\n")
        fp.write("int %s_foo_0() {\n" % (pre_str))
        fp.write("    printf(\"This is the base function\\n\");\n")
        fp.write("    return 0;\n")
        fp.write("}\n\n")
        create_foo(fp, pre_str, max_no, no=no+1)

    else:
        if final_flag:
            fp.write("int %s_foo_begin() {\n" % (pre_str))
            fp.write("    printf(\"This is the begin function %d\\n\");\n" % no)
            fp.write("    %s_foo_%d();\n" % (pre_str, no-1))
            fp.write("    return 0;\n")
            fp.write("}\n\n")

        else:
            fp.write("int %s_foo_%d() {\n" % (pre_str, no))
            fp.write("    printf(\"This is the function %d\\n\");\n" % no)
            fp.write("    %s_foo_%d();\n" % (pre_str, no-1))
            fp.write("    return 0;\n")            
            fp.write("}\n\n")
            create_foo(fp, pre_str, max_no, no=no+1)
    

def main(argv):
    if len(argv) < 1:
        print 'argv number not enough'
        return None
    else:
        global foo_no
        foo_no = int(sys.argv[1])

    div = 10000
    pre_str = "child"
        
    mod = foo_no / div
    print 'create function %d, divid into %d' % (foo_no, mod)

    fpp = init_file("../src/child.c")

    for i in range(0, mod):
        print 'no%d : in range loop %d, mod = %d' % (sys._getframe().f_lineno, i, mod)
        if i == 0:
            print 'no%d : in range loop %d, max_no %d' % (sys._getframe().f_lineno, i, (i+1)*div)
            create_foo(fpp, pre_str, (i+1)*div)
        else:
            print 'no%d : in range loop %d, max_no %d' % (sys._getframe().f_lineno, i, i*div)
            if i != (mod-1):
                create_foo(fpp, pre_str, (i+1) * div, (i*div)+1)
            else:
                print 'no%d : in range loop %d, max_no %d' % (sys._getframe().f_lineno, i, i*div)
                create_foo(fpp, pre_str, (i+1)*div, (i*div)+1, final_flag=True)
    fpp.close()

if __name__ == "__main__":
    main(sys.argv[1:])
        
