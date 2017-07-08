# -*- coding: utf-8 -*-
'''
Created on 8 июл. 2017 г.

@author: krtkr
'''

class Pad(object):
    '''
    Class represents a single pad within a device
    '''
    
    def __init__(self, pad_num, pin, bank, fnc, fnc_opt):
        '''
        Constructor
        '''
        self.pad_num = int(pad_num)
        self.pin = pin
        self.bank = bank
        self.fnc = fnc
        self.fnc_opt = fnc_opt
    
    def not_connected(self):
        if (len(self.pkg_dict) == 0):
            return True
        else:
            return False
    
    def fnc_name(self):
        if len(self.fnc_opt) == 0:
            return self.fnc
        else:
            return self.fnc + "/" + self.fnc_opt
    
    def __repr__(self):
        return str(self.pad_num) + "(" + self.bank + ")@" + self.pin + ":" + self.fnc_name()
    
    def __str__(self):
        return str(self.pad_num) + "@" + self.bank + ":" + self.fnc_name()

class Device(object):
    '''
    Base class representing a single device
    '''
    
    def __init__(self, name):
        '''
        Constructor
        '''
        self.name = name
        self.footprint = 'not set'
        self.fplist = 'not set'
        self.description = 'not set'
        self.search_keys = 'not set'
        self.doc_link = 'not set'
        self.pads = []
    
    def __repr__(self):
        return "Device: " + self.name + " package: " + self.package_name + "pins: " + str(len(self.pads))
    
    def __str__(self):
        return "Device: " + self.name + " package: " + self.package_name + "pins: " + str(len(self.pads))
    

class GenLib(object):
    '''
    Base class for generators
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.__lib_file = None
        self.__dcm_file = None
    
    def open_files(self, lib_file_path, dcm_file_path):
        '''
        Open files for write, existing files will be overwritten!
        '''
        self.__lib_file = open(lib_file_path, "w")
        self.__dcm_file = open(dcm_file_path, "w")
        
        self.__lib_file.write('EESchema-LIBRARY Version 2.3\n')
        self.__lib_file.write('#encoding utf-8\n')
        
        self.__dcm_file.write('EESchema-DOCLIB  Version 2.0\n')
        self.__dcm_file.write('#\n')
    
    def write_device(self, dev):
        '''
        Write device to library, dev should be instance of device class
        '''
        if (self.__lib_file is None or self.__dcm_file is None):
            raise NameError('open files first')
        
        self.__lib_file.write('#\n# ' + dev.name.upper() + '\n#\n')
        self.__lib_file.write('DEF ' + dev.name.upper() + ' U 0 40 Y Y 1 F N\n')
        self.__lib_file.write('F0 "U" 400 700 50 H V L CNN\n')
        self.__lib_file.write('F1 "' + dev.name.upper() + '" 400 600 50 H V L CNN\n')
        self.__lib_file.write('F2 "' + dev.footprint + '" 400 500 50 H I L CNN\n')
        self.__lib_file.write('F3 "" 0 -100 50 H I C CNN\n')
        self.__lib_file.write('$FPLIST\n')
        self.__lib_file.write(' ' + dev.fplist + '\n')
        self.__lib_file.write('$ENDFPLIST\n')
        self.__lib_file.write('DRAW\n')
        # TODO: draw pads properly
        self.__lib_file.write('S -400 600 400 -500 0 1 10 f\n')
        pos = 0
        for pad in dev.pads:
            self.__lib_file.write('X ' + pad.fnc_name() + ' ' + pad.pin + ' -500 ' + str(pos) + ' 100 R 50 50 1 1 I\n')
            pos = pos + 100
        self.__lib_file.write('ENDDRAW\n')
        self.__lib_file.write('ENDDEF\n')
        
        self.__dcm_file.write('$CMP ' + dev.name.upper() + '\n')
        self.__dcm_file.write('D ' + dev.description + '\n')
        self.__dcm_file.write('K ' + dev.search_keys + '\n')
        self.__dcm_file.write('F ' + dev.doc_link + '\n')
        self.__dcm_file.write('$ENDCMP\n')
        self.__dcm_file.write('#\n')
    
    def close_files(self):
        if (self.__lib_file is not None):
            self.__lib_file.write('#\n')
            self.__lib_file.write('#End Library\n')
            self.__lib_file.close()
            self.__lib_file = None
        if (self.__dcm_file is not None):
            self.__dcm_file.write('#End Doc Library\n')
            self.__dcm_file.close()
            self.__dcm_file = None
    
    def __exit__(self):
        self.close_files()
    
