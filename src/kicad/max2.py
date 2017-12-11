# -*- coding: utf-8 -*-
'''
Created on 8 июл. 2017 г.

@author: krtkr
'''

import os
import re
import math
import csv
import operator

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
        "m68":  "68-Pin MBGA",
        "m100": "100-Pin MBGA",
        "m144": "144-Pin MBGA",
        "m256": "256-Pin MBGA",
        "f100": "100-Pin FBGA",
        "f256": "256-Pin FBGA",
        "f324": "324-Pin FBGA",
    }
    __max2_footprints = {
        "t100": "Package_QFP:LQFP-100_14x14mm_P0.5mm",
        "t144": "Package_QFP:LQFP-144_20x20mm_P0.5mm",
        "m68":  "Package_BGA:BGA-68_5.0x5.0mm_Layout9x9_P0.5mm_Ball0.3mm_Pad0.25mm_NSMD",
        "m100": "Package_BGA:BGA-100_6.0x6.0mm_Layout11x11_P0.5mm_Ball0.3mm_Pad0.25mm_NSMD",
        "m144": "Package_BGA:BGA-144_7.0x7.0mm_Layout13x13_P0.5mm_Ball0.3mm_Pad0.25mm_NSMD",
        "m256": "Package_BGA:BGA-256_11.0x11.0mm_Layout20x20_P0.5mm_Ball0.3mm_Pad0.25mm_NSMD",
        "f100": "Package_BGA:BGA-100_11.0x11.0mm_Layout10x10_P1.0mm_Ball0.5mm_Pad0.4mm_NSMD",
        "f256": "Package_BGA:BGA-256_17.0x17.0mm_Layout16x16_P1.0mm_Ball0.5mm_Pad0.4mm_NSMD",
        "f324": "Package_BGA:BGA-324_19.0x19.0mm_Layout18x18_P1.0mm_Ball0.5mm_Pad0.4mm_NSMD",
    }
    __max2_fplists = {
        "t100": " *QFP*P0.5mm*",
        "t144": " *QFP*P0.5mm*",
        "m68":  " *BGA*P0.5mm*",
        "m100": " *BGA*P0.5mm*",
        "m144": " *BGA*P0.5mm*",
        "m256": " *BGA*P0.5mm*",
        "f100": " *BGA*P1.0mm*",
        "f256": " *BGA*P1.0mm*",
        "f324": " *BGA*P1.0mm*",
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
        self.io_pads = []
        self.jtag_pads = []
        self.power_pads = []
    
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
                pad_type = gen.Pad.BIDIR
                bank = io_pin[self.bank_num_idx]
                bank_num_match = re.match('B([0-9])', bank)
                bank_num = None
                if (bank_num_match is not None):
                    bank_num = int(bank_num_match.group(1))
                    if (bank_num % 2):
                        symbol = 'B' + str(bank_num) + '_' + str(bank_num + 1)
                        pad_pos = gen.Pad.POS_LEFT
                    else:
                        symbol = 'B' + str(bank_num - 1) + '_' + str(bank_num)
                        pad_pos = gen.Pad.POS_RIGHT
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
                #m = re.search("^(?P<cnt>[0-9]+).+(?P<tp>MBGA|FBGA|QFP)$", self.__package_name)
                if (not re.match("^(VCC|GND)", fnc) is None):
                    pad_type = gen.Pad.POWER_IN
                    # Move all power pins to power bank
                    if (len(bank) == 0):
                        symbol = 'B1_2'
                    if (not re.match("^VCC", fnc) is None):
                        pad_pos = gen.Pad.POS_TOP
                    else:
                        pad_pos = gen.Pad.POS_BOT
                    dev.power_pads.append(gen.Pad(pad_num, pad_pin_name, symbol, fnc, fnc_opt, pad_type, pad_pos))
                elif (not re.match("^(TCK|TDO|TDI|TMS)$", fnc) is None):
                    if (fnc == 'TCK'):
                        pad_type = gen.Pad.IN_CLK
                    elif (fnc == 'TDO'):
                        pad_type = gen.Pad.OUT
                    else:
                        pad_type = gen.Pad.IN
                    dev.jtag_pads.append(gen.Pad(pad_num, pad_pin_name, symbol, fnc, fnc_opt, pad_type, pad_pos))
                elif (fnc == 'IO'):
                    fnc = 'IO' + str(bank_num) + '_' + pad_pin_name
                    if (not re.match("GCLK", fnc_opt) is None):
                        pad_type = gen.Pad.BIDIR_CLK
                    dev.io_pads.append(gen.Pad(pad_num, pad_pin_name, symbol, fnc, fnc_opt, pad_type, pad_pos))
                else:
                    raise NameError("Unexpected")
        for dev in self.devices_list:
            dev.pads = sorted(dev.io_pads) + dev.jtag_pads + sorted(dev.power_pads, key=operator.attrgetter('fnc'))
    
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
    
