# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

from KicadSymGen.parse import BaseReader, Signal, Device

class Max2Reader(object):
    '''
    Altera MAX2 device tables reader
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        