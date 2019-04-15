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
        self.symbols = None

    def generate(self):
        self.symbols = list()
        dev = self.reader.nextDevice()
        while dev:
            self.parser.parse(dev)
            symbol = Symbol(dev.name)
            for unit in self.parser.units:
                rect = symbol.addRectangle()
                rect.setPos(1, 1)
                for pin in unit:
                    symbol.addDrawing(pin)
            self.symbols.append(symbol)
            dev = self.reader.nextDevice()
        return False
