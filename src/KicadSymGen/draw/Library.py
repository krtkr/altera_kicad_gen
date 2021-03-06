# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

from KicadSymGen.draw import Writer

class Library(object):
    '''
    KiCAD symbol library writer, can output list of symbols into a library.
    '''

    def __init__(self):
        '''
        Constructor
        '''

    def save(self, libFilePath, dcmFilePath, symbolsList):
        writer = Writer(libFilePath, dcmFilePath)
        writer.openFiles()
        for symbol in symbolsList:
            symbol.write(writer)
        writer.closeFiles()
