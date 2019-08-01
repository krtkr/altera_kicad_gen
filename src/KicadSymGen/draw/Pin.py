# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

from KicadSymGen.draw.DrawItem import DrawItem

class Pin(DrawItem):
    '''
    KiCAD Symbol's Pin
    '''

    # Pin share
    PINSHAPE_LINE = ""
    PINSHAPE_INVERTED = "I"
    PINSHAPE_CLOCK = "C"
    PINSHAPE_INVERTED_CLOCK = "IC"
    PINSHAPE_INPUT_LOW = "L"
    PINSHAPE_CLOCK_LOW = "CL"
    PINSHAPE_OUTPUT_LOW = "V"
    PINSHAPE_FALLING_EDGE_CLOCK = "F"
    PINSHAPE_NONLOGIC = "X"

    # Pin type
    PIN_INPUT = 'I'
    PIN_OUTPUT = 'O'
    PIN_BIDI = 'B'
    PIN_TRISTATE = 'T'
    PIN_PASSIVE = 'P'
    PIN_UNSPECIFIED = 'U'
    PIN_POWER_IN = 'W'
    PIN_POWER_OUT = 'w'
    PIN_OPENCOLLECTOR = 'C'
    PIN_OPENEMITTER = 'E'
    PIN_NC = 'N'

    # Pin orientation
    PIN_ORT_LEFT = 'L'
    PIN_ORT_RIGHT = 'R'
    PIN_ORT_TOP = 'U'
    PIN_ORT_BOT = 'D'

    # Some constants from KiCAD source
    DEFAULTPINNUMSIZE = 50
    DEFAULTPINNAMESIZE = 50

    def __init__(self, number, name, unit = 0):
        '''
        Constructor
        position is [x, y] location
        '''
        super(Pin, self).__init__(unit)
        self.position = [0, 0]
        self.length = 100
        self.orientation = Pin.PIN_ORT_RIGHT
        self.shape = Pin.PINSHAPE_LINE
        self.width = 0
        self.pin_type = Pin.PIN_UNSPECIFIED
        self.visible = False
        self.name = name
        self.nameTextSize = Pin.DEFAULTPINNAMESIZE
        self.number = number
        self.numTextSize = Pin.DEFAULTPINNUMSIZE

    def setPos(self, x, y):
        self.position[0] = x
        self.position[1] = y

    def getPosX(self):
        return self.position[0]

    def getPosY(self):
        return self.position[1]

    def setVisibility(self, visible):
        self.visible = visible

    def getPinTypeTab(self):
        return self.pin_type

    def write(self, writer):
        if self.name:
            writer.writeLib("X {:s}".format(self.name))
        else:
            writer.writeLib("X ~")
        if self.number:
            writer.writeLib(" {:s}".format(self.number))
        else:
            writer.writeLib(" ~")
        writer.writeLib(" {:d} {:d} {:d} {:s} {:d} {:d} {:d} {:d} {:s}".format(
            self.getPosX(), self.getPosY(),
            self.length, self.orientation,
            self.numTextSize, self.nameTextSize,
            self.unit, self.convert, self.pin_type))
        if (self.shape or not self.visible):
            writer.writeLib(" ")
        if (not self.visible):
            writer.writeLib("N")
        if (self.shape):
            writer.writeLib(self.shape)
        writer.writeLib("\n")
