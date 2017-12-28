# -*- coding: utf-8 -*-
'''
Created on 20 июл. 2017 г.

@author: krtkr
'''

import os
import re
import csv
import operator

import gen

class Max10Device(gen.Device):
    '''
    max10 class contains altera max10 devices related logic and settings
    '''

    expected_header = [
        'Bank Number',
        'VREF',
        'Pin Name/Function',
        'Optional Function(s)',
        'Configuration Function',
        'Dedicated Tx/Rx Channel',
        'Emulated LVDS Output Channel',
        'IO Performance',
        ]
    
    BANK = 0
    VREF = 1
    PIN_FNC = 2
    PIN_OPT_FNC = 3
    PIN_CFG_FNC = 4
    TX_RX_CH = 5
    LVDS = 6
    IO_PERF = 7
    PIN_PAD = 8
    DDR_X8 = 9
    DDR_X16 = 10
    
    expected_packages = [
        'U324',
        'V36',
        'E144',
        'M153',
        'U169',
        'F256',
        'F484',
        'V81',
        'F672'
        ]
    
    __max10_footprints = {
        "E144": "Package_QFP:LQFP-144-1EP_20x20mm_P0.5mm_EP[size_mm]x[size_mm]mm",
        "M153": "Package_BGA:BGA-153_8.0x8.0mm_Layout15x15_P0.5mm_Ball0.3mm_Pad0.25mm_NSMD",
        "F256": "Package_BGA:BGA-256_17.0x17.0mm_Layout16x16_P1.0mm_Ball0.5mm_Pad0.4mm_NSMD",
        "F484": "Package_BGA:BGA-484_23.0x23.0mm_Layout22x22_P1.0mm_Ball0.6mm_Pad0.5mm_NSMD",
        "F672": "Package_BGA:BGA-672_27.0x27.0mm_Layout26x26_P1.0mm_Ball0.6mm_Pad0.5mm_NSMD",
        "V36" : "Package_BGA:BGA-36_3.396x3.466mm_Layout6x6_P0.4mm_Ball0.25mm_Pad0.2mm_NSMD",
        "V81" : "Package_BGA:BGA-81_4.496x4.377mm_Layout9x9_P0.4mm_Ball0.25mm_Pad0.2mm_NSMD",
        "U169": "Package_BGA:BGA-169_11.0x11.0mm_Layout13x13_P0.8mm_Ball0.5mm_Pad0.4mm_NSMD",
        "U324": "Package_BGA:BGA-324_15.0x15.0mm_Layout18x18_P0.8mm_Ball0.5mm_Pad0.4mm_NSMD",
    }
    
    __max10_fplists = {
        "E144": " *QFP*P0.5mm*EP[size_mm]x[size_mm]mm*",
        "M153": " *BGA*P0.5mm*",
        "F256": " *BGA*P1.0mm*",
        "F484": " *BGA*P1.0mm*",
        "F672": " *BGA*P1.0mm*",
        "V36" : " *BGA*P0.4mm*",
        "V81" : " *BGA*P0.4mm*",
        "U169": " *BGA*P0.8mm*",
        "U324": " *BGA*P0.8mm*",
    }
    
    __max10_e144_ep_sizes = {
        "10M02" : "4",
        "10M04" : "5",
        "10M08" : "5",
        "10M16" : "6.61",
        "10M25" : "7.2",
        "10M40" : "8.93",
        "10M50" : "8.93",
    }
    
    __max10_family_descriptions = {
        'SA' : 'Single supply, analog and flash features with RSU option',
        'SC' : 'Single supply, compact features FPGA',
        'DA' : 'Dual supply, compact features',
        'DC' : 'Dual supply, compact features',
        'DF' : 'Dual supply, flash features with RSU option',
    }
    __max10_package_descriptions = {
        "E144": ", TQFP package",
        "M153": ", MBGA package",
        "F256": ", FBGA package",
        "F484": ", FBGA package",
        "F672": ", FBGA package",
        "V36" : ", WLCSP package",
        "V81" : ", WLCSP package",
        "U169": ", UBGA package",
        "U324": ", UBGA package",
    }
    
    __max10_family_search_keys = {
        'SA' : 'Single supply FPGA RSU Analog',
        'SC' : 'Single supply FPGA',
        'DA' : 'Dual supply FPGA RSU Analog',
        'DC' : 'Dual supply FPGA',
        'DF' : 'Dual supply FPGA RSU',
    }
    __max10_package_search_keys = {
        "E144": " TQFP",
        "M153": " MBGA",
        "F256": " FBGA",
        "F484": " FBGA",
        "F672": " FBGA",
        "V36" : " WLCSP",
        "V81" : " WLCSP",
        "U169": " UBGA",
        "U324": " UBGA",
    }
    
    def __init__(self, name, family_name, package_name, header, pins_table):
        super(Max10Device, self).__init__(name)
        self.header = header
        self.pins_table = pins_table
        self.footprint = self.__max10_footprints[package_name]
        self.fplist = self.__max10_fplists[package_name]
        self.description = self.__max10_family_descriptions[family_name] + self.__max10_package_descriptions[package_name]
        self.search_keys = self.__max10_family_search_keys[family_name] + self.__max10_package_search_keys[package_name]
        self.doc_link = 'https://www.altera.com/content/dam/altera-www/global/en_US/pdfs/literature/hb/max-10/m10_handbook.pdf'
        self.io_pads = {}
        self.dedicated_pads = []
        self.power_pads = []
        if (package_name == "E144"):
            # E144 packages use different EP size depend on LE count
            e144_match = re.match("(10M[0-9]{2})", name)
            if (e144_match is None):
                raise NameError("Unable to parse device name: " + name)
            self.footprint = re.sub("\[size_mm\]", self.__max10_e144_ep_sizes[e144_match.group(1)], self.footprint)
            self.fplist = re.sub("\[size_mm\]", self.__max10_e144_ep_sizes[e144_match.group(1)], self.fplist)
            self.power_pads.append(gen.Pad(-1, "145", "COMMON", "GND", "", gen.Pad.POWER_IN, gen.Pad.POS_BOT))
    
    def parse_pins_table(self):
        might_have_ddr8 = len(self.header) > self.DDR_X8
        might_have_ddr16 = len(self.header) > self.DDR_X16
        if (len(self.header) > self.DDR_X16 + 1):
            raise NameError("Unexpected columns count for device " + self.name)
        for pin_row in self.pins_table:
            # To simplify work with a row copy cells into named variables
            io_bank = pin_row[self.BANK]
            vref_group = pin_row[self.VREF]
            pin_fnc = pin_row[self.PIN_FNC]
            pin_opt_fnc = pin_row[self.PIN_OPT_FNC]
            pin_cfg_fnc = pin_row[self.PIN_CFG_FNC]
            tx_rx_ch = pin_row[self.TX_RX_CH]
            lvds = pin_row[self.LVDS]
            io_perf = pin_row[self.IO_PERF]
            pin_pad = pin_row[self.PIN_PAD]
            if (not self.io_pads.has_key(io_bank)):
                self.io_pads[io_bank] = []
            symbol = "COMMON"
            if pin_fnc[0] == 'I':
                pad_type = gen.Pad.BIDIR
                pad_name = pin_fnc + io_bank
                if (len(lvds)):
                    lvds_match = re.match("DIFFOUT_([A-Za-z0-9]+)", lvds)
                    if (lvds_match is None):
                        raise NameError("Unable to parse LVDS signa description  " + lvds + " for device " + self.name)
                    pad_name = pad_name + "_" + lvds_match.group(1)
                pad_name = pad_name + "_" + pin_pad
                if (len(pin_opt_fnc) != 0):
                    pad_name = pad_name + "/" + pin_opt_fnc
                if (might_have_ddr8):
                    if (len(pin_row[self.DDR_X8]) != 0):
                        pad_name = pad_name + "/" + pin_row[self.DDR_X8]
                if (might_have_ddr16):
                    if (len(pin_row[self.DDR_X16]) != 0):
                        pad_name = pad_name + "/" + pin_row[self.DDR_X16]
                if (len(pin_cfg_fnc) != 0):
                    pad_name = pad_name + "/" + pin_cfg_fnc
#                    pad_pos = gen.Pad.POS_LEFT
#                    self.dedicated_pads.append(gen.Pad(-1, pin_pad, symbol, pad_name, "", pad_type, pad_pos))
#                else:
                pad_pos = gen.Pad.POS_RIGHT
                self.io_pads[io_bank].append(gen.Pad(-1, pin_pad, symbol, pad_name, "", pad_type, pad_pos))
            else:
                pad_type = gen.Pad.POWER_IN
                pad_name = pin_fnc
                if pin_fnc[0:3] == 'VCC':
                    pad_pos = gen.Pad.POS_TOP
                elif pin_fnc == 'NC':
                    continue
                else:
                    pad_pos = gen.Pad.POS_BOT
                self.power_pads.append(gen.Pad(-1, pin_pad, symbol, pad_name, "", pad_type, pad_pos))
        banks = sorted(self.io_pads.keys())
        halfcount = len(self.io_pads.keys())/2 + 1
        i = 0
        for bank in banks:
            io_pads = self.io_pads[bank]
            if (i < halfcount):
                for pads in io_pads:
                    pads.pad_pos = gen.Pad.POS_LEFT
            i = i + 1
            self.pads = self.pads + io_pads
        # First sort by pin name
        self.power_pads = sorted(self.power_pads)
        self.pads = self.pads + sorted(self.power_pads, key=operator.attrgetter('fnc'))


class Max10Parser(object):
    '''
    MAX 10 Parser: able to create a list of avaiable devices and fill it
    '''
    
    def __init__(self, max10_pinouts_path):
        '''
        Constructor
        '''
        self.pinouts_path = max10_pinouts_path
        self.dev_list = []
        # For debug purposes, collect list of packages
        self.packages_list = []
    
    def find_devices(self):
        max10_device_files = [f for f in os.listdir(self.pinouts_path) if os.path.isfile(os.path.join(self.pinouts_path, f))]
        for device_file_path in sorted(max10_device_files):
            device_file = open(os.path.join(self.pinouts_path, device_file_path), 'r')
            csv_reader = csv.reader(device_file, delimiter='\t')
            first_row = None
            header = None
            device_prefix = None
            package_name = None
            family_name = None
            expected_pins_count = 0
            pins_table = []
            for row in csv_reader:
                if (len(row) == 0):
                    continue
                if (first_row is None):
                    dev_match = re.search("Pin Information for the.+(10M[0-9]{2}(SA|SC|DA|DC|DF))", row[0])
                    if (dev_match is not None):
                        first_row = row
                        device_prefix = dev_match.group(1)
                        family_name = dev_match.group(2)
                    continue
                if (header is None):
                    if (len(Max10Device.expected_header) > len(row)):
                        continue
                    for i in range(len(Max10Device.expected_header)):
                        if (Max10Device.expected_header[i] != row[i]):
                            row = None
                            break
                    if (row is None):
                        continue
                    header = row
                    if (len(header) < len(Max10Device.expected_header) + 1):
                        print header
                        print Max10Device.expected_header
                        raise NameError("Seems that package name is missing at file " + device_file_path)
                    package_name_match = re.match('([A-Z][0-9]+)', header[len(Max10Device.expected_header)])
                    if (package_name_match is None):
                        raise NameError("Unable to parse package name '" + header[len(Max10Device.expected_header)] + "' at file" + device_file_path)
                    package_name = package_name_match.group(1)
                    if (not package_name in self.packages_list):
                        self.packages_list.append(package_name)
                    # Self check, just to make sure we parse file correctly
                    pins_count_match = re.match('[A-Z]([0-9]+)', package_name)
                    if (pins_count_match is None):
                        raise NameError("Unable to parse package name: " + package_name)
                    expected_pins_count = int(pins_count_match.group(1))
                    continue
                if (re.match("Note.+", row[0]) is not None or len(header) > len(row)):
                    if (expected_pins_count != len(pins_table)):
                        raise NameError("Expected " + str(expected_pins_count) + " pins for package " + package_name + " at file " + device_file_path + " but found " + str(len(pins_table)))
                    self.dev_list.append(Max10Device(device_prefix + package_name, family_name, package_name, header, pins_table))
                    first_row = None
                    header = None
                    device_prefix = None
                    package_name = None
                    family_name = None
                    expected_pins_count = 0
                    pins_table = []
                else:
                    pins_table.append(row)
        # Debug check
        if (len(Max10Device.expected_packages) != len(self.packages_list)):
            raise NameError("Extra packages found. Expected: " + str(Max10Device.expected_packages) + " got: " + str(self.packages_list))
        for package in self.packages_list:
            if not package in Max10Device.expected_packages:
                raise NameError("Unexpected package " + package + " expected list: " + str(Max10Device.expected_packages))
    
    def parse_pinouts(self):
        for dev in self.dev_list:
            dev.parse_pins_table()
    

class Max10GenLib(gen.GenLib):
    '''
    MAX 10 Library Generator class
    '''
    
    def __init__(self, max10_pinouts_path):
        '''
        Constructor
        '''
        super(Max10GenLib, self).__init__()
        self.parser = Max10Parser(max10_pinouts_path)
    
    def generate(self, lib_file_path, dcm_file_path, verbose = False):
        if (verbose):
            print "path: " + self.parser.pinouts_path
            print "lib file: " + lib_file_path
            print "dcm file: " + dcm_file_path
        self.parser.find_devices()
        if (verbose):
            print "Found " + str(len(self.parser.packages_list)) + " packages: " + str(self.parser.packages_list)
            print "Total devices found: " + str(len(self.parser.dev_list))
            for dev in self.parser.dev_list:
                print " - " + dev.name
        self.parser.parse_pinouts()
        super(Max10GenLib, self).open_files(lib_file_path, dcm_file_path)
        for dev in self.parser.dev_list:
            super(Max10GenLib, self).write_device(dev)
        super(Max10GenLib, self).close_files()
    
