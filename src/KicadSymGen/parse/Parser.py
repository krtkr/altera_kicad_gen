'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

class Parser(object):
    '''
    Parser class is used to read data from device table/vendor documentation
    using specific Device Reader, link signal properties to Units and Pins
    according to parsing rules
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        
