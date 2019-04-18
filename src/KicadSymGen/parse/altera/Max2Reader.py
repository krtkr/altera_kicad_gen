# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

import os
import csv
import re
import math

import KicadSymGen.parse

class Max2Device(KicadSymGen.parse.Device):
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
        self.addProp("footprint", pkg_info[1])
        self.addProp("fplist", pkg_info[2])
        self.addProp("description", description)
        self.addProp("search_keys", search_keys)
        self.addProp("doc_link", 'https://www.altera.com/content/dam/altera-www/global/en_US/pdfs/literature/hb/max2/max2_mii5v1.pdf')
        self.addProp("package_name", pkg_info[0])
    
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
                    KicadSymGen.parse.util.binary_insert(pins, i + str(j+1))
        elif mbga:
            side_cnt = cnt/16 + 4
            for i in range(side_cnt):
                inside_i = i > 3 and i < side_cnt-4
                i = self.__bga_letters[i]
                for j in range(side_cnt):
                    inside = inside_i and j > 3 and j < side_cnt-4
                    if (inside):
                        continue
                    KicadSymGen.parse.util.binary_insert(pins, i + str(j+1))
        else:
            for i in range(cnt):
                KicadSymGen.parse.binary_insert(pins, str(i))
        
        for pad in self.pads:
            KicadSymGen.parse.util.binary_del(pins, pad.pin)
        
        return pins

class Max2Reader(object):
    '''
    Altera MAX2 device tables reader
    '''
    
    __bank_num_head = 'Bank Number'
    __pad_num_head = 'Pad Number Orientation'
    __pad_fnc_head = 'Pin/Pad Function'
    __pad_opt_fnc_head = 'Optional Function(s)'
    
    def __init__(self, max2_pinouts_path):
        
        '''
        Constructor
        '''
        self.max2_pinouts_path = max2_pinouts_path
        
        self.dev_dict = dict()
        
        self.dev_dict['epm240'] = [
                Max2Device("epm240t100", "Altera MAX2 CPLD with 240 LE", "MAX2 TQFP"),
                Max2Device("epm240f100", "Altera MAX2 CPLD with 240 LE", "MAX2 FBGA"),
                Max2Device("epm240m100", "Altera MAX2 CPLD with 240 LE", "MAX2 MBGA")]
        self.dev_dict['epm240z'] = [
                Max2Device("epm240zm68", "Altera Zero-Power MAX2 CPLD with 240 LE", "MAX2 MBGA"),
                Max2Device("epm240zm100", "Altera Zero-Power MAX2 CPLD with 240 LE", "MAX2 MBGA")]
        self.dev_dict['epm570'] = [
                Max2Device("epm570t100", "Altera MAX2 CPLD with 570 LE", "MAX2 TQFP"),
                Max2Device("epm570f100", "Altera MAX2 CPLD with 570 LE", "MAX2 FBGA"),
                Max2Device("epm570m100", "Altera MAX2 CPLD with 570 LE", "MAX2 MBGA"),
                Max2Device("epm570t144", "Altera MAX2 CPLD with 570 LE", "MAX2 TQFP"),
                Max2Device("epm570f256", "Altera MAX2 CPLD with 570 LE", "MAX2 FBGA"),
                Max2Device("epm570f256", "Altera MAX2 CPLD with 570 LE", "MAX2 FBGA"),
                Max2Device("epm570m256", "Altera MAX2 CPLD with 570 LE", "MAX2 MBGA")]
        self.dev_dict['epm570z'] = [
                Max2Device("epm570zm100", "Altera Zero-Power MAX2 CPLD with 570 LE", "MAX2 MBGA"),
                Max2Device("epm570zm144", "Altera Zero-Power MAX2 CPLD with 570 LE", "MAX2 MBGA"),
                Max2Device("epm570zm256", "Altera Zero-Power MAX2 CPLD with 570 LE", "MAX2 MBGA")]
        self.dev_dict['epm1270'] = [
                Max2Device("epm1270t144", "Altera MAX2 CPLD with 1270 LE", "MAX2 TQFP"),
                Max2Device("epm1270f256", "Altera MAX2 CPLD with 1270 LE", "MAX2 FBGA"),
                Max2Device("epm1270m256", "Altera MAX2 CPLD with 1270 LE", "MAX2 MBGA")]
        self.dev_dict['epm2210'] = [
                Max2Device("epm2210f256", "Altera MAX2 CPLD with 2210 LE", "MAX2 FBGA"),
                Max2Device("epm2210f324", "Altera MAX2 CPLD with 2210 LE", "MAX2 FBGA")]
        self.dev_prefix = None
        self.dev_list = None

    def __read_io_file(self):
        io_file_path = self.dev_prefix + "-io_s.txt"
        io_file_path = os.path.join(self.max2_pinouts_path, io_file_path)
        io_file = open(io_file_path, "r")
        io_csv = csv.reader(io_file, delimiter = "\t")
        header = next(io_csv)
        header_len = 0
        self.io_header = []
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
            if len(head) == 0:
                break
            else:
                self.io_header.append(head)
                header_len += 1
        self.io_table = []
        for row in io_csv:
            row = row[0:header_len]
            self.io_table.append(row)
    
    def __find_dev_io_idx(self, dev_package_name):
        dev_index = None
        index = 0
        for head in self.io_header:
            if head == dev_package_name:
                dev_index = index
                break
            index += 1
        return dev_index
    
    def __read_dedicated_file(self):
        dedicated_file_path = self.dev_prefix + "-dedicated_s.txt"
        dedicated_file_path = os.path.join(self.max2_pinouts_path, dedicated_file_path)
        dedicated_file = open(dedicated_file_path, "r")
        dedicated_csv = csv.reader(dedicated_file, delimiter = "\t")
        header = next(dedicated_csv)
        header_len = 0
        self.dedicated_header = []
        for head in header:
            head = head.strip(' ')
            if len(head) == 0:
                break
            elif head == "Dedicated Pin":
                continue
            else:
                self.dedicated_header.append(head)
                header_len += 1
        self.dedicated_table = {}
        for row in dedicated_csv:
            m = re.search("(?P<pin_name>[A-Za-z0-9/_ ]+)", row[0])
            pin_name = m.group("pin_name")
            pin_name = pin_name.strip(' ')
            ''' To be compatible with KiCAD conventions'''
            if (pin_name == "No Connect"):
                pin_name = "NC"
            self.dedicated_table[pin_name] = []
            for cell in row[1:header_len + 1]:
                cell = cell.replace('"', '')
                cell = cell.replace(' ', '')
                cell = cell.replace('.', ',')
                cell = cell.split(",")
                self.dedicated_table[pin_name].append(cell)
    
    def __find_dev_dedicated_idx(self, dev_package_name):
        dev_index = None
        index = 0
        for head in self.dedicated_header:
            if head == dev_package_name:
                dev_index = index
                break
            index += 1
        return dev_index

    def nextDevice(self):
        if self.dev_list is None:
            if self.dev_dict is None:
                return None
            else:
                (self.dev_prefix, self.dev_list) = self.dev_dict.popitem()
                if len(self.dev_dict) == 0:
                    self.dev_dict = None
                self.__read_io_file()
                self.__read_dedicated_file()
        max2_dev = self.dev_list.pop()
        if len(self.dev_list) == 0:
            self.dev_list = None
        max2_io_idx = self.__find_dev_io_idx(max2_dev.getPropsDict()["package_name"])
        max2_d_idx = self.__find_dev_dedicated_idx(max2_dev.getPropsDict()["package_name"])
        for io_pin in self.io_table:
            pad_pin_name = io_pin[max2_io_idx]
            fnc = io_pin[self.pad_fnc_idx]
            if len(pad_pin_name) == 0:
                ''' Search for pad in dedicated list '''
                if fnc not in self.dedicated_table:
                    continue
                if len(self.dedicated_table[fnc][max2_d_idx]) != 0:
                    pad_pin_name = self.dedicated_table[fnc][max2_d_idx].pop(0)
                else:
                    continue
            signal = KicadSymGen.parse.Signal(fnc)
            signal.addProp("pad_num", io_pin[self.pad_num_idx])
            signal.addProp("pad_pin_name", pad_pin_name)
            signal.addProp("bank", io_pin[self.bank_num_idx])
            signal.addProp("fnc", fnc)
            signal.addProp("fnc_opt", io_pin[self.pad_opt_fnc_idx]) 
            signal.addProp("pad_pin_name", pad_pin_name)
            max2_dev.addSignal(signal)
        return max2_dev
