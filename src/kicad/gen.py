# -*- coding: utf-8 -*-
'''
Created on 8 июл. 2017 г.

@author: krtkr
'''

import re

class Pad(object):
    '''
    Class represents a single pad within a device
    '''
    
    # TODO: How to create Enums in python? :D
    # Represents pad types
    POWER_IN = 1
    BIDIR = 2
    BIDIR_CLK = 3
    IN = 4
    IN_CLK = 5
    OUT = 6
    NO_CONNECT = 7
    
    # Represents pad position
    POS_LEFT = 0
    POS_RIGHT = 1
    POS_TOP = 2
    POS_BOT = 3
    
    def __init__(self, pad_num, pin, bank, fnc, fnc_opt, pad_type = BIDIR, pad_pos = POS_RIGHT):
        '''
        Constructor
        '''
        self.pad_num = int(pad_num)
        self.__pin = '0'
        self.__pin_value = 0
        self.pin = pin
        self.bank = bank
        self.fnc = fnc
        self.fnc_opt = fnc_opt
        self.pad_type = pad_type
        self.pad_pos = pad_pos
        # This flag determines whether 
        self.write_to_file = True
    
    @property
    def pin(self):
        return self.__pin
    
    @pin.setter
    def pin(self, value):
        pin_match = re.match("^([A-Z]+)([0-9]+)", value)
        if (pin_match is None):
            self.__pin_value = int(value)
        else:
            self.__pin_value = int(pin_match.group(2))
            letters_part = pin_match.group(1)
            letters_count = len(letters_part)
            for i in range(1, letters_count + 1):
                letter_value = ord(letters_part[letters_count - i])
                letter_value = letter_value << (8 * i)
                self.__pin_value = self.__pin_value + letter_value
        self.__pin = value
    
    def __lt__(self, other):
        return self.__pin_value < other.__pin_value
    
    def __gt__(self, other):
        return self.__pin_value > other.__pin_value
    
    def __eq__(self, other):
        return self.__pin_value == other.__pin_value
    
    def __le__(self, other):
        return self.__pin_value <= other.__pin_value
    
    def __ge__(self, other):
        return self.__pin_value >= other.__pin_value
    
    def __ne__(self, other):
        return self.__pin_value != other.__pin_value
    
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
    

class SymbolUnit(object):
    '''
    Class represents a single symbol unit
    '''
    
    def __init__(self, bank):
        self.bank = bank
        self.__pins_count = [0, 0, 0, 0]
        self.__max_pin_name_lens = [0, 0, 0, 0]
    
    def update_max_pin_name_len(self, pin_name_len, pin_pos):
        self.__max_pin_name_lens[pin_pos] = max([
                pin_name_len,
                self.__max_pin_name_lens[pin_pos],
            ])
    
    def get_max_left_pin_name_len(self):
        return self.__max_pin_name_lens[Pad.POS_LEFT]
    
    def get_max_right_pin_name_len(self):
        return self.__max_pin_name_lens[Pad.POS_RIGHT]
    
    def get_max_top_pin_name_len(self):
        return self.__max_pin_name_lens[Pad.POS_TOP]
    
    def get_max_bot_pin_name_len(self):
        return self.__max_pin_name_lens[Pad.POS_BOT]
    
    def get_pins_left(self):
        return self.__pins_count[Pad.POS_LEFT]
    
    def get_pins_right(self):
        return self.__pins_count[Pad.POS_RIGHT]
    
    def get_pins_top(self):
        return self.__pins_count[Pad.POS_TOP]
    
    def get_pins_bot(self):
        return self.__pins_count[Pad.POS_BOT]
    
    def inc_pins(self, pin_pos):
        self.__pins_count[pin_pos] = self.__pins_count[pin_pos] + 1
    
    def get_max_pins_horizontal(self):
        return max([self.__pins_count[Pad.POS_TOP], self.__pins_count[Pad.POS_BOT]])
    
    def get_max_pins_vertical(self):
        return max([self.__pins_count[Pad.POS_LEFT], self.__pins_count[Pad.POS_RIGHT]])


class GenLib(object):
    '''
    Base class for generators
    '''
    # W for power input
    # B for bidirectional
    # B C for bidir clock
    # I for input
    # I C for clock input
    # O for output

    __kicad_types = {
        Pad.POWER_IN : 'W',
        Pad.BIDIR : 'B',
        Pad.BIDIR_CLK : 'B C',
        Pad.IN : 'I',
        Pad.IN_CLK : 'I C',
        Pad.OUT : 'O',
        Pad.NO_CONNECT : 'N N'
        }
    
    # Map pin position on symbol to pin orientation
    __kicad_orient = {
        Pad.POS_BOT : 'U',
        Pad.POS_LEFT : 'R',
        Pad.POS_RIGHT : 'L',
        Pad.POS_TOP : 'D',
        }
    
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
        
        banks_stats = {}
        max_pin_len = 0
        # Interate first time over pad to get required for symbol generation info
        for pad in dev.pads:
            if (not banks_stats.has_key(pad.bank)):
                banks_stats[pad.bank] = SymbolUnit(pad.bank)
            banks_stats[pad.bank].inc_pins(pad.pad_pos)
            if (pad.write_to_file):
                banks_stats[pad.bank].update_max_pin_name_len(len(pad.fnc_name()), pad.pad_pos)
            max_pin_len = max([
                    max_pin_len,
                    len(pad.pin)
                ])
        
        # Per dev variables
        units_count = len(banks_stats)
        pin_length = (max_pin_len + 1) * 50
        
        # Calculate symbol height
        symbol_height = 0
        for bank in sorted(banks_stats.keys()):
            symbol_unit = banks_stats[bank]
            symbol_height = max([
                    symbol_height,
                    (symbol_unit.get_max_pins_vertical() + 1) * 100,
                    (symbol_unit.get_max_top_pin_name_len() + 1) * 100,
                    (symbol_unit.get_max_bot_pin_name_len() + 1) * 100,
                ])
        
        # Calculate symbol width
        symbol_width = 0
        top_right_symbol_max = 0
        bot_right_symbol_max = 0
        for bank in sorted(banks_stats.keys()):
            symbol_unit = banks_stats[bank]
            
            pos_top = -(symbol_unit.get_pins_top() - 1) * 50
            if (pos_top % 100):
                pos_top = pos_top - 50
            pos_bot = -(symbol_unit.get_pins_bot() - 1) * 50
            if (pos_bot % 100):
                pos_bot = pos_bot - 50
            
            top_left = (-pos_top) + 50
            bot_left = (-pos_bot) + 50
            top_right = pos_top + (symbol_unit.get_pins_top() - 1) * 100 + 50
            bot_right = pos_bot + (symbol_unit.get_pins_bot() - 1) * 100 + 50
            top_max = symbol_unit.get_max_top_pin_name_len() * 50
            bot_max = symbol_unit.get_max_bot_pin_name_len() * 50
            left_max = symbol_unit.get_max_left_pin_name_len() * 50
            right_max = symbol_unit.get_max_right_pin_name_len() * 50
            right_top_pins = left_top_pins = top_max / 100
            left_top_max = 0
            right_top_max = 0
            
            top_right_symbol_max = max([
                    top_right_symbol_max,
                    top_right,
                ])
            bot_right_symbol_max = max([
                    bot_right_symbol_max,
                    bot_right,
                ])
            
            for pad in dev.pads:
                if (pad.bank == bank):
                    if (pad.pad_pos == Pad.POS_LEFT and left_top_pins != 0):
                        left_top_pins = left_top_pins - 1
                        left_top_max = max([
                                left_top_max,
                                len(pad.fnc_name()),
                            ])
                    if (pad.pad_pos == Pad.POS_RIGHT and right_top_pins != 0):
                        right_top_pins = right_top_pins - 1
                        right_top_max = max([
                                right_top_max,
                                len(pad.fnc_name()),
                            ])
                    if (left_top_pins == 0 and right_top_pins == 0):
                        break
            
            left_top_max = left_top_max * 50
            right_top_max = right_top_max * 50
            
            if (symbol_height < symbol_unit.get_pins_left() * 100 + bot_max):
                left_bot_pins = ((symbol_unit.get_pins_left() * 100 + bot_max) - symbol_height) / 100
            else:
                left_bot_pins = 0
            
            if (symbol_height < symbol_unit.get_pins_right() * 100 + bot_max):
                right_bot_pins = ((symbol_unit.get_pins_right() * 100 + bot_max) - symbol_height) / 100
            else:
                right_bot_pins = 0
            
            left_bot_max = 0
            right_bot_max = 0
            for pad in reversed(dev.pads):
                if (pad.bank == bank):
                    if (pad.pad_pos == Pad.POS_LEFT and left_bot_pins != 0):
                        left_bot_pins = left_bot_pins - 1
                        left_bot_max = max([
                                left_bot_max,
                                len(pad.fnc_name()),
                            ])
                    if (pad.pad_pos == Pad.POS_RIGHT and right_bot_pins != 0):
                        right_bot_pins = right_bot_pins - 1
                        right_bot_max = max([
                                right_bot_max,
                                len(pad.fnc_name()),
                            ])
                    if (left_bot_pins == 0 and right_bot_pins == 0):
                        break
            
            left_bot_max = (left_bot_max + 1) * 50
            right_bot_max = (right_bot_max + 1) * 50
            
            left = max([
                    left_max,
                    left_top_max + top_left,
                    left_bot_max + bot_left,
                ])
            
            right = max([
                    right_max,
                    right_top_max + top_right,
                    right_bot_max + bot_right,
                ])
            
            symbol_width = max([
                    symbol_width,
                    2*left,
                    2*right,
                    (symbol_unit.get_max_left_pin_name_len() + 1) * 100,
                    (symbol_unit.get_max_right_pin_name_len() + 1) * 100,
                ])
        
        # Make symbol_height multiple of 200
        if (symbol_height % 200):
            symbol_height = symbol_height + 100
        # Make symbol wigth multiple of 100
        if (symbol_width % 100):
            symbol_width = symbol_width + 50
        
        pos_left_base = symbol_height / 2 - 100
        pos_right_base = symbol_height / 2 - 100
        
        if (symbol_width/2 + pin_length) % 100:
            symbol_width = symbol_width + 100
        if (symbol_height/2 + pin_length) % 100:
            symbol_height = symbol_height + 100
        
        # Calculated parameters
        refdes_pos = [top_right_symbol_max + 50, 50 + symbol_height/2]
        name_pos = [bot_right_symbol_max + 50, -50 - symbol_height/2]
        footprints_pos = [bot_right_symbol_max + 50, -150 - symbol_height/2]
        
        self.__lib_file.write('#\n# ' + dev.name.upper() + '\n#\n')
        self.__lib_file.write('DEF ' + dev.name.upper() + ' U 0 40 Y Y ' + str(units_count) + ' L N\n')
        self.__lib_file.write('F0 "U" ' + str(refdes_pos[0]) + ' ' + str(refdes_pos[1]) + ' 50 H V L CNN\n')
        self.__lib_file.write('F1 "' + dev.name.upper() + '" ' + str(name_pos[0]) + ' ' + str(name_pos[1]) + ' 50 H V L CNN\n')
        self.__lib_file.write('F2 "' + dev.footprint + '" ' + str(footprints_pos[0]) + ' ' + str(footprints_pos[1]) + ' 50 H I L CNN\n')
        self.__lib_file.write('F3 "" 0 0 50 H I C CNN\n')
        self.__lib_file.write('$FPLIST\n')
        self.__lib_file.write(' ' + dev.fplist + '\n')
        self.__lib_file.write('$ENDFPLIST\n')
        self.__lib_file.write('DRAW\n')
        
        unit = 1
        for bank in sorted(banks_stats.keys()):
            symbol_unit = banks_stats[bank]
            # Calculate base pin offsets
            pos_left = pos_left_base
            pos_right = pos_right_base
            pos_top = -(symbol_unit.get_pins_top() - 1) * 50
            if (pos_top % 100):
                pos_top = pos_top - 50
            pos_bot = -(symbol_unit.get_pins_bot() - 1) * 50
            if (pos_bot % 100):
                pos_bot = pos_bot - 50
            # According to KLC we use 100mil grid, pin origin must lie on grid nodes (IEC-60617):
            self.__lib_file.write('S ' + str(-symbol_width/2) + ' ' + str(symbol_height/2) + ' ' + str(symbol_width/2) + ' ' + str(-symbol_height/2) + ' ' + str(unit) + ' 1     0 f\n')
            for pad in dev.pads:
                if (pad.bank == bank):
                    if (pad.pad_pos == Pad.POS_BOT):
                        pin_pos = [pos_bot, -symbol_height/2 - pin_length]
                        pos_bot = pos_bot + 100
                    elif (pad.pad_pos == Pad.POS_LEFT):
                        pin_pos = [-symbol_width/2 - pin_length, pos_left]
                        pos_left = pos_left - 100
                    elif (pad.pad_pos == Pad.POS_RIGHT):
                        pin_pos = [symbol_width/2 + pin_length, pos_right]
                        pos_right = pos_right - 100
                    elif (pad.pad_pos == Pad.POS_TOP):
                        pin_pos = [pos_top, symbol_height/2 + pin_length]
                        pos_top = pos_top + 100
                    if (pad.write_to_file):
                        self.__lib_file.write('X ' + pad.fnc_name() + ' ' + pad.pin + ' ' + str(pin_pos[0]) + ' ' + str(pin_pos[1]) + ' ' + str(pin_length) + ' ' + self.__kicad_orient[pad.pad_pos] + ' 50 50 ' + str(unit) + ' 1 ' + self.__kicad_types[pad.pad_type] + '\n')
            unit = unit + 1
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
    
