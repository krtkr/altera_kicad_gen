'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

class Device(object):
    '''
    This class represents a device as it have parsed from documentation, add
    all properties that you have into device
    '''

    __props = dict()
    __signals = list()

    def __init__(self, name):
        '''
        Constructor
        '''
        

    def addProp(self, name, value):
        self.__props[name] = value

    def getPropsDict(self):
        return self.__props

    def addSignal(self, signal):
        self.__signals.append(signal)

    def getSignalsList(self):
        return self.__signals
