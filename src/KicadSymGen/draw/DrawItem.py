'''
Created on 19 июн. 2019 г.

@author: krtkr
'''

class DrawItem(object):
    '''
    classdocs
    '''

    NO_FILL = 'N'
    FILLED_SHAPE = 'F'
    FILLED_WITH_BG_BODYCOLOR = 'f'

    def __init__(self, unit = 0, convert = 0, filltype = NO_FILL):
        self.unit = unit
        self.convert = convert
        self.filltype = filltype

    def getFillMode(self):
        return self.filltype
