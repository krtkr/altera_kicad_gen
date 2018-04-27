'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

from KicadSymGen import BaseReader, Generator, Signal

class Max2Reader(object):
    '''
    Altera MAX2 device tables reader
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        