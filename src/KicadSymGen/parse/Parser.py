# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

import re

class Parser(object):
    '''
    Parser class is used to  link signal properties from device to Units and Pins
    according to parsing rules
    '''

    def __init__(self, rules):
        '''
        Constructor
        '''
        
        self.rules = rules
        self.units = None
        '''
        Precompile regexps at specified
        '''
        # TODO: ...

    '''
    Parse next device using self.rules
    '''
    def parse(self, device):
        self.units = list(list())

