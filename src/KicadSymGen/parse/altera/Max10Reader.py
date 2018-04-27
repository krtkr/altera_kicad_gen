'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

from KicadSymGen import BaseReader, Generator, Signal

class Max10Reader(BaseReader):
    '''
    Intel (former Altera) MAX10 device tables reader
    '''


    def __init__(self, max10_pinouts_path):
        '''
        Constructor
        '''
        

    def nextDevice(self):
        return None

    def nextSignal(self):
        return None