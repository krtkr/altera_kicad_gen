# -*- coding: utf-8 -*-
'''
Created on 8 июл. 2017 г.

@author: krtkr
'''

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
    
    # Represents pad position
    POS_LEFT = 1
    POS_RIGHT = 2
    POS_TOP = 3
    POS_BOT = 4
    
    def __init__(self, pad_num, pin, bank, fnc, fnc_opt, pad_type = BIDIR, pad_pos = POS_RIGHT):
        '''
        Constructor
        '''
        self.pad_num = int(pad_num)
        self.pin = pin
        self.bank = bank
        self.fnc = fnc
        self.fnc_opt = fnc_opt
        self.pad_type = pad_type
        self.pad_pos = pad_pos
        # This flag determines whether 
        self.write_to_file = True
    
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
        self.__pins_top = 0
        self.__pins_bot = 0
        self.__pins_left = 0
        self.__pins_right = 0
        self.__pins_horizontal = 0
        self.__pins_vertical = 0
    
    def get_pins_top(self):
        return self.__pins_top
    
    def inc_pins_top(self):
        self.__pins_top = self.__pins_top + 1
        if (self.__pins_top > self.__pins_bot):
            self.__pins_horizontal = self.__pins_top
    
    def get_pins_bot(self):
        return self.__pins_bot
    
    def inc_pins_bot(self):
        self.__pins_bot = self.__pins_bot + 1
        if (self.__pins_bot > self.__pins_top):
            self.__pins_horizontal = self.__pins_bot
    
    def get_pins_left(self):
        return self.__pins_left
    
    def inc_pins_left(self):
        self.__pins_left = self.__pins_left + 1
        if (self.__pins_left > self.__pins_right):
            self.__pins_vertical = self.__pins_left
    
    def get_pins_right(self):
        return self.__pins_right
    
    def inc_pins_right(self):
        self.__pins_right = self.__pins_right + 1
        if (self.__pins_right > self.__pins_left):
            self.__pins_vertical = self.__pins_right
    
    def get_pins_horizontal(self):
        return self.__pins_horizontal
    
    def get_pins_vertical(self):
        return self.__pins_vertical


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
        max_horizontal_pins = 0
        min_horizontal_pins = 65535
        max_vertical_pins = 0
        min_vertical_pins = 65535
        max_left_pin_name_len = 0
        max_right_pin_name_len = 0
        # Interate first time over pad to get required for symbol generation info
        for pad in dev.pads:
            if (not banks_stats.has_key(pad.bank)):
                banks_stats[pad.bank] = SymbolUnit(pad.bank)
            if (pad.pad_pos == Pad.POS_BOT):
                banks_stats[pad.bank].inc_pins_bot()
            elif (pad.pad_pos == Pad.POS_LEFT):
                banks_stats[pad.bank].inc_pins_left()
                max_left_pin_name_len = max([
                        max_left_pin_name_len,
                        len(pad.fnc_name())
                    ])
            elif (pad.pad_pos == Pad.POS_RIGHT):
                banks_stats[pad.bank].inc_pins_right()
                max_right_pin_name_len = max([
                        max_right_pin_name_len,
                        len(pad.fnc_name())
                    ])
            elif (pad.pad_pos == Pad.POS_TOP):
                banks_stats[pad.bank].inc_pins_top()
            else:
                raise NameError("Unexpected value at pad.pad_pos")
        for symbol_unit in banks_stats.values():
            max_horizontal_pins = max([
                max_horizontal_pins,
                symbol_unit.get_pins_horizontal(),
                ])
            min_horizontal_pins = min([
                min_horizontal_pins,
                symbol_unit.get_pins_horizontal()
                ])
            max_vertical_pins = max([
                max_vertical_pins,
                symbol_unit.get_pins_vertical(),
                ])
            min_vertical_pins = min([
                min_vertical_pins,
                symbol_unit.get_pins_vertical()
                ])
        
        # Per dev variables
        units_count = len(banks_stats)
        symbol_zero_offset = ((min_vertical_pins + 2) * 100) / 2
        symbol_width = max([
                ((max_horizontal_pins + 2) * 100) + 200,
                ((max_left_pin_name_len + max_right_pin_name_len + 2) + 1) / 2 * 2 * 50
            ])
        # Preset parameters
        pin_length = 150
        # Calculated parameters
        refdes_pos = [-symbol_width/2 + 50, symbol_zero_offset + 50]
        name_pos = [0, symbol_zero_offset + 50]
        footprints_pos = [-symbol_width/2 + 50, symbol_zero_offset + 150]
        
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
            # Per unit variables
            current_symbol_size = [symbol_width, (symbol_unit.get_pins_vertical() + 1) * 100]
            self.__lib_file.write('S ' + str(-current_symbol_size[0]/2) + ' ' + str(symbol_zero_offset) + ' ' + str(current_symbol_size[0]/2) + ' ' + str(symbol_zero_offset - current_symbol_size[1]) + ' ' + str(unit) + ' 1     0 f\n')
            pos_left = symbol_zero_offset - 100
            pos_right = symbol_zero_offset - 100
            pos_top = -(symbol_unit.get_pins_top() - 1) * 50
            pos_bot = -(symbol_unit.get_pins_bot() - 1) * 50
            for pad in dev.pads:
                if (pad.bank == bank):
                    if (pad.pad_pos == Pad.POS_BOT):
                        pin_pos = [pos_bot, symbol_zero_offset - current_symbol_size[1] - pin_length]
                        pos_bot = pos_bot + 100
                    elif (pad.pad_pos == Pad.POS_LEFT):
                        pin_pos = [-symbol_width/2 - pin_length, pos_left]
                        pos_left = pos_left - 100
                    elif (pad.pad_pos == Pad.POS_RIGHT):
                        pin_pos = [symbol_width/2 + pin_length, pos_right]
                        pos_right = pos_right - 100
                    elif (pad.pad_pos == Pad.POS_TOP):
                        pin_pos = [pos_top, symbol_zero_offset + pin_length]
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
    
