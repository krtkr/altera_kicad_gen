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

    def __init__(self, reader, parse_rules, layout):
        '''
        Constructor
        '''
        self.reader = reader
        self.parser = Parser(parse_rules)
        self.layout = layout
        self.layout.prepare()
        self.symbols = None

    def generate(self):
        self.symbols = list()
        dev = self.reader.nextDevice()
        while dev:
            self.parser.parse(dev)
            symbol = Symbol(dev.name)
            symbol.referenceField().value = self.getReferenceField(dev)
            symbol.valueField().value = self.getValueField(dev)
            symbol.footprintField().value = self.getFootprintField(dev)
            symbol.datasheetField().value = self.getDatasheetField(dev)
            for unit in self.parser.units:
                rect = symbol.addRectangle()
                rect.setPos(1, 1)
                for pin in unit:
                    symbol.addDrawing(pin)
            self.symbols.append(symbol)
            dev = self.reader.nextDevice()
        return True

    def getReferenceField(self, dev):
        t = self.layout.v_ReferenceField
        v = self.layout.replace(t, dev, None)
        return v

    def getValueField(self, dev):
        t = self.layout.v_ValueField
        v = self.layout.replace(t, dev, None)
        return v

    def getFootprintField(self, dev):
        t = self.layout.v_FootprintField
        v = self.layout.replace(t, dev, None)
        return v

    def getDatasheetField(self, dev):
        t = self.layout.v_DatasheetField
        v = self.layout.replace(t, dev, None)
        return v
