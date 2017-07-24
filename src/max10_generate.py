# -*- coding: utf-8 -*-
'''
Created on 20 июл. 2017 г.

@author: krtkr
'''

import kicad.max10
import sys
import getopt

def print_help():
    print 'test.py -p <pinouts_path> -d <dcm_file> -l <lib_file>'

if __name__ == '__main__':
    verbose = False
    pinouts_path = "../docs/max10"
    dcm_file_path = './max10.dcm'
    lib_file_path = './max10.lib'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvp:d:l:",["pinouts=","dcm=","lib="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt == '-v':
            verbose = True
        elif opt in ("-p", "--pinouts"):
            pinouts_path = arg
        elif opt in ("-d", "--dcm_file"):
            dcm_file_path = arg
        elif opt in ("-l", "--lib_file"):
            lib_file_path = arg
    max10_gen_lib = kicad.max10.Max10GenLib(pinouts_path)
    max10_gen_lib.generate(lib_file_path, dcm_file_path, verbose)
    pass