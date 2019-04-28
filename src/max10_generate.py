# -*- coding: utf-8 -*-
'''
Created on 20 июл. 2017 г.

@author: krtkr
'''

import sys
import getopt

from KicadSymGen.draw import Library
from KicadSymGen.generate import Generator
from KicadSymGen.generate import Layout

from KicadSymGen.parse.altera import Max10Reader
from KicadSymGen.parse.altera import Max10Parser

def print_help():
    print('max10_generate.py -p <pinouts_path> -d <dcm_file> -l <lib_file>')

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

    parse = Max10Parser(list())
    layout = Layout()

    max10Reader = Max10Reader(pinouts_path)
    generator = Generator(max10Reader, parse, layout)
    if generator.generate():
        library = Library()
        library.save(lib_file_path, dcm_file_path, generator.symbols)
    else:
        print("Error: failed to generate")
    pass
