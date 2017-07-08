# -*- coding: utf-8 -*-
'''
Created on 8 июл. 2017 г.

@author: krtkr
'''

import os
import re
import math
import csv

import gen
import util

class Max2Device(gen.Device):
    '''
    max2 class contains altera max2 devices related logic and settings
    '''

    __bga_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'T', 'U', 'V', 'W', 'Y', 'AA', 'AB']
    __max2_packages = {
        "t100": "100-Pin TQFP",
        "t144": "144-Pin TQFP",
        "m68": "68-Pin MBGA",
        "m100": "100-Pin MBGA",
        "m144": "144-Pin MBGA",
        "m256": "256-Pin MBGA",
        "f100": "100-Pin FBGA",
        "f256": "256-Pin FBGA",
        "f324": "324-Pin FBGA",
    }
    __max2_footprints = {
        "t100": "100-Pin TQFP",
        "t144": "144-Pin TQFP",
        "m68": "68-Pin MBGA",
        "m100": "100-Pin MBGA",
        "m144": "144-Pin MBGA",
        "m256": "256-Pin MBGA",
        "f100": "100-Pin FBGA",
        "f256": "256-Pin FBGA",
        "f324": "324-Pin FBGA",
    }
    __max2_fplists = {
        "t100": "100-Pin TQFP",
        "t144": "144-Pin TQFP",
        "m68": "68-Pin MBGA",
        "m100": "100-Pin MBGA",
        "m144": "144-Pin MBGA",
        "m256": "256-Pin MBGA",
        "f100": "100-Pin FBGA",
        "f256": "256-Pin FBGA",
        "f324": "324-Pin FBGA",
    }
    
    def __init__(self, name, description, search_keys):
        '''
        Constructor
        '''
        super(Max2Device, self).__init__(name)
        pkg_info = self.__find_pkg_info()
        self.footprint = pkg_info[1]
        self.fplist = pkg_info[2]
        self.description = description
        self.search_keys = search_keys
        self.doc_link = 'https://www.altera.com/content/dam/altera-www/global/en_US/pdfs/literature/hb/max2/max2_mii5v1.pdf'
        self.package_name = pkg_info[0]
        self.package_io_idx = -1
        self.package_dedicated_idx = -1
    
    def __find_pkg_info(self):
        '''
        Find Altera's package name for a Max2Device name
        '''
        m = re.search("^(?P<dev>.+)(?P<pkg>[a-z][0-9]+)$", self.name)
        package_suffix = m.group("pkg")
        return [self.__max2_packages[package_suffix], self.__max2_footprints[package_suffix], self.__max2_fplists[package_suffix]]
    
    def find_lost_pins(self):
        '''
        Find lost pins - function used only for debug purposes, used to find which pins has not been parsed
        '''
        m = re.search("^(?P<cnt>[0-9]+).+(?P<tp>MBGA|FBGA|QFP)$", self.__package_name)
        fbga = m.group("tp") == "FBGA"
        mbga = m.group("tp") == "MBGA"
        cnt = int(m.group("cnt"))
        if len(self.pads) == cnt:
            return None
        
        ''' Generate list of pins '''
        pins = []
        if fbga:
            side_cnt = int(math.sqrt(cnt))
            for i in range(side_cnt):
                i = self.__bga_letters[i]
                for j in range(side_cnt):
                    util.binary_insert(pins, i + str(j+1))
        elif mbga:
            side_cnt = cnt/16 + 4
            for i in range(side_cnt):
                inside_i = i > 3 and i < side_cnt-4
                i = self.__bga_letters[i]
                for j in range(side_cnt):
                    inside = inside_i and j > 3 and j < side_cnt-4
                    if (inside):
                        continue
                    util.binary_insert(pins, i + str(j+1))
        else:
            for i in range(cnt):
                util.binary_insert(pins, str(i))
        
        for pad in self.pads:
            util.binary_del(pins, pad.pin)
        
        return pins

class Max2Parser(object):
    '''
    classdocs
    '''
    
    __bank_num_head = 'Bank Number'
    __pad_num_head = 'Pad Number Orientation'
    __pad_fnc_head = 'Pin/Pad Function'
    __pad_opt_fnc_head = 'Optional Function(s)'
    
    def __init__(self, devices_list, io_file_path, dedicated_file_path):
        '''
        Constructor
        '''
        self.devices_list = devices_list
        self.io_file_path = io_file_path
        self.dedicated_file_path = dedicated_file_path
        self.bank_num_idx = -1
        self.pad_num_idx = -1
        self.pad_fnc_idx = -1
        self.pad_opt_fnc_idx = -1
    
    def __parse_io_file(self):
        io_file = open(self.io_file_path, "r")
        io_csv = csv.reader(io_file, delimiter = "\t")
        header = io_csv.next()
        header_len = 0
        for head in header:
            head = head.strip(' ')
            if head == self.__bank_num_head:
                self.bank_num_idx = header_len
            if head == self.__pad_num_head:
                self.pad_num_idx = header_len
            if head == self.__pad_fnc_head:
                self.pad_fnc_idx = header_len
            if head == self.__pad_opt_fnc_head:
                self.pad_opt_fnc_idx = header_len
            for dev in self.devices_list:
                if head == dev.package_name:
                    dev.package_io_idx = header_len
            if len(head) == 0:
                break
            else:
                header_len += 1
        self.io_header = header[0:header_len]
        self.io_table = []
        for row in io_csv:
            row = row[0:header_len]
            self.io_table.append(row)
    
    def __parse_dedicated_file(self):
        dedicated_file = open(self.dedicated_file_path, "r")
        dedicated_csv = csv.reader(dedicated_file, delimiter = "\t")
        header = dedicated_csv.next()
        header_len = 0
        for head in header:
            head = head.strip(' ')
            for dev in self.devices_list:
                if head == dev.package_name:
                    dev.package_dedicated_idx = header_len - 1
            if len(head) == 0:
                break
            else:
                header_len += 1
        self.dedicated_header = header[1:header_len]
        self.dedicated_table = {}
        for row in dedicated_csv:
            m = re.search("(?P<pin_name>[A-Za-z0-9/_ ]+)", row[0])
            pin_name = m.group("pin_name")
            pin_name = pin_name.strip(' ')
            ''' To be compatible with KiCAD conventions'''
            if (pin_name == "No Connect"):
                pin_name = "NC"
            self.dedicated_table[pin_name] = []
            for cell in row[1:header_len]:
                cell = cell.replace('"', '')
                cell = cell.replace(' ', '')
                cell = cell.replace('.', ',')
                cell = cell.split(",")
                self.dedicated_table[pin_name].append(cell)
    
    def __create_pads_table(self):
        for io_pin in self.io_table:
            for dev in self.devices_list:
                pad_num = io_pin[self.pad_num_idx]
                pad_pin_name = io_pin[dev.package_io_idx]
                bank = io_pin[self.bank_num_idx]
                if len(bank) == 0:
                    bank = 'POWER'
                fnc = io_pin[self.pad_fnc_idx]
                fnc_opt = io_pin[self.pad_opt_fnc_idx]
                if len(pad_pin_name) == 0:
                    ''' Search for pad in dedicated list '''
                    if not self.dedicated_table.has_key(fnc):
                        continue
                    if len(self.dedicated_table[fnc][dev.package_dedicated_idx]) != 0:
                        pad_pin_name = self.dedicated_table[fnc][dev.package_dedicated_idx].pop(0)
                    else:
                        continue
                dev.pads.append(gen.Pad(pad_num, pad_pin_name, bank, fnc, fnc_opt))
        ''' Add NC pins '''
        if self.dedicated_table.has_key("NC"):
            for dev in self.devices_list:
                if len(self.dedicated_table["NC"][dev.package_dedicated_idx]) != 0 and self.dedicated_table["NC"][dev.package_dedicated_idx][0] != "-":
                    for nc_pin in self.dedicated_table["NC"][dev.package_dedicated_idx]:
                        dev.pads.append(gen.Pad(-1, nc_pin, "NC", "NC", ""))
    
    def parse_pinouts(self):
        self.__parse_io_file()
        self.__parse_dedicated_file()
        self.__create_pads_table()
    

class Max2AllDevices(object):
    '''
    Class with lists of all available max2 devices
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.max240 = [
                Max2Device("epm240t100", "Altera MAX2 CPLD with 240 LE", "MAX2 TQFP"),
                Max2Device("epm240f100", "Altera MAX2 CPLD with 240 LE", "MAX2 FBGA"),
                Max2Device("epm240m100", "Altera MAX2 CPLD with 240 LE", "MAX2 MBGA"),
            ]
        
        self.max240z = [
                Max2Device("epm240zm68", "Altera Zero-Power MAX2 CPLD with 240 LE", "MAX2 MBGA"),
                Max2Device("epm240zm100", "Altera Zero-Power MAX2 CPLD with 240 LE", "MAX2 MBGA"),
            ]
        
        self.max570 = [
                Max2Device("epm570t100", "Altera MAX2 CPLD with 570 LE", "MAX2 TQFP"),
                Max2Device("epm570f100", "Altera MAX2 CPLD with 570 LE", "MAX2 FBGA"),
                Max2Device("epm570m100", "Altera MAX2 CPLD with 570 LE", "MAX2 MBGA"),
                Max2Device("epm570t144", "Altera MAX2 CPLD with 570 LE", "MAX2 TQFP"),
                Max2Device("epm570f256", "Altera MAX2 CPLD with 570 LE", "MAX2 FBGA"),
                Max2Device("epm570m256", "Altera MAX2 CPLD with 570 LE", "MAX2 MBGA"),
            ]
        
        self.max570z = [
                Max2Device("epm570zm100", "Altera Zero-Power MAX2 CPLD with 570 LE", "MAX2 MBGA"),
                Max2Device("epm570zm144", "Altera Zero-Power MAX2 CPLD with 570 LE", "MAX2 MBGA"),
                Max2Device("epm570zm256", "Altera Zero-Power MAX2 CPLD with 570 LE", "MAX2 MBGA"),
            ]
        
        self.max1270 = [
                Max2Device("epm1270t144", "Altera MAX2 CPLD with 1270 LE", "MAX2 TQFP"),
                Max2Device("epm1270f256", "Altera MAX2 CPLD with 1270 LE", "MAX2 FBGA"),
                Max2Device("epm1270m256", "Altera MAX2 CPLD with 1270 LE", "MAX2 MBGA"),
            ]
        
        self.max2210 = [
                Max2Device("epm2210f256", "Altera MAX2 CPLD with 2210 LE", "MAX2 FBGA"),
                Max2Device("epm2210f324", "Altera MAX2 CPLD with 2210 LE", "MAX2 FBGA"),
            ]

class Max2GenLib(gen.GenLib):
    '''
    Class with lists of all available max2 devices
    '''
    
    def __init__(self, max2_pinouts_path):
        '''
        Constructor
        '''
        super(Max2GenLib, self).__init__()
        self.__max2_all_devices = Max2AllDevices()
        
        self.__max2_parsers = [
            Max2Parser(self.__max2_all_devices.max240, os.path.join(max2_pinouts_path, "epm240-io_s.txt"), os.path.join(max2_pinouts_path, "epm240-dedicated_s.txt")),
            Max2Parser(self.__max2_all_devices.max240z, os.path.join(max2_pinouts_path, "epm240z-io_s.txt"), os.path.join(max2_pinouts_path, "epm240z-dedicated_s.txt")),
            Max2Parser(self.__max2_all_devices.max570, os.path.join(max2_pinouts_path, "epm570-io_s.txt"), os.path.join(max2_pinouts_path, "epm570-dedicated_s.txt")),
            Max2Parser(self.__max2_all_devices.max570z, os.path.join(max2_pinouts_path, "epm570z-io_s.txt"), os.path.join(max2_pinouts_path, "epm570z-dedicated_s.txt")),
            Max2Parser(self.__max2_all_devices.max1270, os.path.join(max2_pinouts_path, "epm1270-io_s.txt"), os.path.join(max2_pinouts_path, "epm1270-dedicated_s.txt")),
            Max2Parser(self.__max2_all_devices.max2210, os.path.join(max2_pinouts_path, "epm2210-io_s.txt"), os.path.join(max2_pinouts_path, "epm2210-dedicated_s.txt")),
        ]
    
    def __parse(self, verbose = False):
        for parser in self.__max2_parsers:
            parser.parse_pinouts()
            if verbose:
                for dev in parser.devices_list:
                    print dev
                    print dev.pads
                    lost_pins = dev.find_lost_pins()
                    print lost_pins
    
    def generate(self, lib_file_path, dcm_file_path, verbose = False):
        self.__parse(verbose)
        super(Max2GenLib, self).open_files(lib_file_path, dcm_file_path)
        for parser in self.__max2_parsers:
            for dev in parser.devices_list:
                super(Max2GenLib, self).write_device(dev)
        super(Max2GenLib, self).close_files()
    
