# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

import os
import csv
import re

import KicadSymGen.parse

class Max10Reader(KicadSymGen.parse.BaseReader):
    '''
    Intel (former Altera) MAX10 device tables reader
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
        'SA' : 'Single supply - analog and flash features with RSU option',
        'SC' : 'Single supply - compact features',
        'DA' : 'Dual supply - analog and flash features with RSU option',
        'DC' : 'Dual supply - compact features',
        'DF' : 'Dual supply - flash features with RSU option',
    }
    
    __max10_package_descriptions = {
        "E144": "TQFP-144",
        "M153": "MBGA-153",
        "F256": "FBGA-256",
        "F484": "FBGA-484",
        "F672": "FBGA-672",
        "V36" : "WLCSP-36",
        "V81" : "WLCSP-81",
        "U169": "UBGA-169",
        "U324": "UBGA-324",
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
    
    __max10_member_code = {
        "10M02" : "2K logic elements",
        "10M04" : "4K logic elements",
        "10M08" : "8K logic elements",
        "10M16" : "16K logic elements",
        "10M25" : "25K logic elements",
        "10M40" : "40K logic elements",
        "10M50" : "50K logic elements",
    }

    def __init__(self, max10_pinouts_path):
        '''
        Constructor
        '''
        self.max10_pinouts_path = max10_pinouts_path
        self.max10_device_files = [f for f in os.listdir(max10_pinouts_path) if os.path.isfile(os.path.join(max10_pinouts_path, f))]
        self.max10_device_files.sort(reverse=True)
        self.device_file_fd = None
        self.packages_list = list()

    def nextDevice(self):
        max10_dev = None
        if self.device_file_fd:
            self.device_file_fd.close()
            self.device_file_fd = None
        if len(self.max10_device_files):
            device_file_path = self.max10_device_files.pop()
            device_file_path = os.path.join(self.max10_pinouts_path, device_file_path)
            print("Processing file {:s}".format(device_file_path))
            self.device_file_fd = open(device_file_path, 'r', encoding="ISO-8859-1")
            csv_reader = csv.reader(self.device_file_fd, delimiter='\t')
            first_row = None
            header = None
            device_prefix = None
            package_name = None
            family_name = None
            expected_pins_count = 0
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
                    if (len(self.expected_header) > len(row)):
                        continue
                    for i in range(len(self.expected_header)):
                        if (self.expected_header[i] != row[i]):
                            row = None
                            break
                    if (row is None):
                        continue
                    header = row
                    if (len(header) < len(self.expected_header) + 1):
                        print(header)
                        print(self.expected_header)
                        raise NameError("Package name is missing at file " + device_file_path)
                    package_name_match = re.match('([A-Z][0-9]+)', header[len(self.expected_header)])
                    if (package_name_match is None):
                        raise NameError("Unable to parse package name '" + header[len(self.expected_header)] + "' at file" + device_file_path)
                    package_name = package_name_match.group(1)
                    if (not package_name in self.packages_list):
                        self.packages_list.append(package_name)
                    # Self check, just to make sure we parse file correctly
                    pins_count_match = re.match('[A-Z]([0-9]+)', package_name)
                    if (pins_count_match is None):
                        raise NameError("Unable to parse pins count: " + package_name)
                    expected_pins_count = int(pins_count_match.group(1))
                    max10_dev = KicadSymGen.parse.Device(device_prefix + package_name)
                    max10_dev.addProp("device_prefix", device_prefix)
                    max10_dev.addProp("family_name", family_name)
                    max10_dev.addProp("package_name", package_name)
                    max10_dev.addProp("header", header)
                    continue
                if (re.match("Note.+", row[0]) is not None or len(header) > len(row)):
                    if (expected_pins_count != len(max10_dev.getSignalsList())):
                        raise NameError("Expected " + str(expected_pins_count) + " pins for package " + package_name + " at file " + device_file_path + " but found " + str(len(max10_dev.getSignalsList())))
                    break;
                else:
                    signal = KicadSymGen.parse.Signal(row[Max10Reader.PIN_FNC])
                    for n, v in zip(header, row):
                        signal.addProp(n, v)
                    max10_dev.addSignal(signal)
        return max10_dev
