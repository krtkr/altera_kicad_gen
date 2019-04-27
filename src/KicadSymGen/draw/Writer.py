# -*- coding: utf-8 -*-
'''
Created on 27 апр. 2018 г.

@author: krtkr
'''

class Writer(object):
    '''
    Write library
    '''

    LIB_VERSION_MAJOR = 2
    LIB_VERSION_MINOR = 4
    LIBFILE_IDENT = "EESchema-LIBRARY Version"
    DOCFILE_IDENT = "EESchema-DOCLIB  Version 2.0"

    def __init__(self, libFilePath, dcmFilePath):
        '''
        Constructor
        '''
        self.__libFilePath = libFilePath
        self.__dcmFilePath = dcmFilePath
        self.__libFile = None
        self.__dcmFile = None

    def openFiles(self):
        '''
        Open files for write, existing files will be overwritten!
        '''
        self.__libFile = open(self.__libFilePath, "w")
        self.__dcmFile = open(self.__dcmFilePath, "w")
        
        self.__libFile.write("{:s} {:d}.{:d}\n".format(Writer.LIBFILE_IDENT, Writer.LIB_VERSION_MAJOR, Writer.LIB_VERSION_MINOR))
        self.__libFile.write('#encoding utf-8\n')
        
        self.__dcmFile.write('{:s}\n'.format(Writer.DOCFILE_IDENT))
        self.__dcmFile.write('#\n')

    def closeFiles(self):
        if (self.__libFile is not None):
            self.__libFile.write('#\n')
            self.__libFile.write('#End Library\n')
            self.__libFile.close()
            self.__libFile = None
        if (self.__dcmFile is not None):
            self.__dcmFile.write('#End Doc Library\n')
            self.__dcmFile.close()
            self.__dcmFile = None

    def writeLib(self, data):
        self.__libFile.write(data)

    def writeDcm(self, data):
        self.__dcmFile.write(data)

