# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

from KicadSymGen.parse import Parser
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
            for unit in self.parser.units:
                rect = symbol.addRectangle()
                rect.setPos(1, 1)
                for pin in unit:
                    symbol.addDrawing(pin)
            self.symbols.append(symbol)
            dev = self.reader.nextDevice()
        return True
