# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

class Signal(object):
    '''
    This class represents a single signal description with properties dict
    as it has been parsed from documentation
    '''

    def __init__(self, name):
        '''
        Constructor
        '''
        self.__props = dict()
        self.name = name

    def __getitem__(self, key):
        return self.__props[key]

    def addProp(self, name, value):
        self.__props[name] = value

    def getPropsDict(self):
        return self.__props
