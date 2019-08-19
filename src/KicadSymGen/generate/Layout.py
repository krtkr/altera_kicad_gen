# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

class Layout(object):
    '''
    Symbol layout kind. This class describe how pins should be distributed
    between Units, within Unit etc
    '''

    SORT_NO_SORT = 0
    SORT_PIN_NAME = 1
    SORT_PIN_NUMBER = 2

    def __init__(self):
        '''
        Constructor
        '''
        self.sort_units = Layout.SORT_NO_SORT
        self.sort_last_unit = Layout.SORT_NO_SORT
        self.stack_power_pins = 0
