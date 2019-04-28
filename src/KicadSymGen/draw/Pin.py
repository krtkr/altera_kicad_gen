# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

class Pin(object):
    '''
    KiCAD Symbol's Pin
    '''

    # Pin share
    PINSHAPE_LINE = 1
    PINSHAPE_INVERTED = 2
    PINSHAPE_CLOCK = 3
    PINSHAPE_INVERTED_CLOCK = 4
    PINSHAPE_INPUT_LOW = 5
    PINSHAPE_CLOCK_LOW = 6
    PINSHAPE_OUTPUT_LOW = 7
    PINSHAPE_FALLING_EDGE_CLOCK = 8
    PINSHAPE_NONLOGIC = 9

    # Pin type
    PIN_INPUT = 1
    PIN_OUTPUT = 2
    PIN_BIDI = 3
    PIN_TRISTATE = 4
    PIN_PASSIVE = 5
    PIN_UNSPECIFIED = 6
    PIN_POWER_IN = 7
    PIN_POWER_OUT = 8
    PIN_OPENCOLLECTOR = 9
    PIN_OPENEMITTER = 10
    PIN_NC = 11

    # Pin orientation
    PIN_ORT_LEFT = 1
    PIN_ORT_RIGHT = 2
    PIN_ORT_TOP = 3
    PIN_ORT_BOT = 4

    def __init__(self, number, name):
        '''
        Constructor
        position is [x, y] location
        '''
        self.position = [0, 0]
        self.length = 100
        self.orientation = Pin.PIN_ORT_RIGHT
        self.shape = Pin.PINSHAPE_LINE
        self.width = 0
        self.pin_type = Pin.PIN_UNSPECIFIED
        self.visible = False
        self.name = name
        self.number = number

    def setPos(self, x, y):
        self.position[0] = x
        self.position[1] = y

    def getPosX(self):
        return self.position[0]

    def getPosY(self):
        return self.position[1]

    def setVisibility(self, visible):
        self.visible = visible
