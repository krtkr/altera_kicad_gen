# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

from KicadSymGen.draw import Symbol

class Generator(object):
    '''
    This class generates Symbols using selected Parser and Layout.
    '''

    def __init__(self, reader, parser, layout):
        '''
        Constructor
        '''
        self.reader = reader
        self.parser = parser
        self.parser.prepare()
        self.layout = layout
        self.symbols = None

    def generate(self):
        self.symbols = list()
        dev = self.reader.nextDevice()
        while dev:
            self.parser.parse(dev)
            symbol = Symbol(dev.name)
            symbol.pinNameOffset = self.parser.pinNameOffset
            symbol.referenceField().value = self.parser.referenceField
            symbol.valueField().value = self.parser.valueField
            symbol.footprintField().value = self.parser.footprintField
            symbol.datasheetField().value = self.parser.datasheetField
            symbol.setDescription(self.parser.description)
            symbol.setKeyWords(self.parser.keyWords)
            symbol.setDocFileName(self.parser.docFileName)
            unit_idx = 0
            symbol.unitCount = len(self.parser.units)
            for unit in self.parser.units:
                unit_idx = unit_idx + 1
                rect = symbol.addRectangle()
                rect.unit = unit_idx
                pins_list = list()
                pins_longest_name_len = 0
                for sig in unit:
                    pin = symbol.addPin(
                            self.parser.getPinNumber(dev, sig),
                            self.parser.getPinName(dev, sig))
                    pin.unit = unit_idx
                    pins_list.append(pin)
                    pins_longest_name_len = max(pins_longest_name_len, len(pin.name))

                ''' Sort pins '''
                if (unit_idx == symbol.unitCount):
                    sort_units = self.layout.sort_last_unit
                else:
                    sort_units = self.layout.sort_units

                if (sort_units == self.layout.SORT_PIN_NAME):
                    pins_list = sorted(pins_list, key=lambda pin: pin.name)
                elif (sort_units == self.layout.SORT_PIN_NUMBER):
                    pins_list = sorted(pins_list, key=lambda pin: pin.number)

                ''' Bank label if any '''
                bank_label = self.parser.getBankLabel(dev, sig)
                if (bank_label):
                    pins_longest_name_len = pins_longest_name_len + 100

                ''' Calculate symbol geometry '''
                pins_count = len(unit)
                # TODO: allow pin stacking here
                pin_y = pins_count / 2.0 * 100.0
                pin_y = int(pin_y) - 50
                # Find nearest lager even number
                pins_longest_name_len = int((pins_longest_name_len + 1) / 2) * 2

                sym_width = max(pins_longest_name_len * 50, 300)
                sym_width = int(sym_width/2)
                rect.setPos(sym_width, pin_y + 100)
                rect.setEnd(-sym_width,-pin_y - 100)

                ''' Place pins '''
                for pin in pins_list:
                    pin.setPos(-sym_width-pin.length, pin_y)
                    pin_y = pin_y - 100
                    pin.convert = 1
                    pin.visible = 1
                    pin.pin_type = self.parser.getPinType(dev, sig)
                    pin.shape = self.parser.getPinShape(dev, sig)
            self.symbols.append(symbol)
            dev = self.reader.nextDevice()
        return True
