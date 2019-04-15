# -*- coding: utf-8 -*-
'''
Created on 26 апр. 2018 г.

@author: krtkr
'''

class Rectangle(object):
    '''
    KiCAD Symbol library draw item: rectangle
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.position = [0, 0]
        self.end = [0, 0]

    def setPos(self, x, y):
        self.position[0] = x
        self.position[1] = y

    def getPosX(self):
        return self.position[0]

    def getPosY(self):
        return self.position[1]

    def setEnd(self, x, y):
        self.end[0] = x
        self.end[1] = y

    def getEndX(self):
        return self.end[0]

    def getEndY(self):
        return self.end[1]
