'''
Created on 27 апр. 2018 г.

@author: krtkr
'''

class Field(object):
    '''
    KiCAD Field
    '''

    '''
    Field Reference of part, i.e. "IC21"
    '''
    REFERENCE = 0
    '''
    Field Value of part, i.e. "3.3K"
    ''' 
    VALUE = 1 
    '''
    Field Name Module PCB, i.e. "16DIP300"
    '''
    FOOTPRINT = 2
    '''
    name of datasheet
    '''
    DATASHEET = 3

    HJUSTIFY_CENTER = 'C'
    HJUSTIFY_LEFT = 'L'
    HJUSTIFY_RIGHT = 'R'

    VJUSTIFY_CENTER = 'C'
    VJUSTIFY_BOTTOM = 'B'
    VJUSTIFY_TOP = 'T'

    ANGLE_HORIZONTAL = 'H'
    ANGLE_VERTICAL = 'V'

    def __init__(self, type, value = ""):
        '''
        Constructor
        '''
        self.type = type
        self.value = value
        self.position = [0, 0]
        self.width = 50
        self.angle = Field.ANGLE_HORIZONTAL
        self.visible = True
        self.hjustify = Field.HJUSTIFY_CENTER
        self.vjustify = Field.VJUSTIFY_CENTER
        self.italic = False
        self.bold = False

    def setPos(self, x, y):
        self.position[0] = x
        self.position[1] = y

    def getPosX(self):
        return self.position[0]

    def getPosY(self):
        return self.position[1]

    def write(self, writer):
        writer.writeLib(
            "F{:d} {:s} {:d} {:d} {:d} {:s} {:s} {:s} {:s}{:s}{:s}\n".format(
                self.type,
                self.value,
                self.getPosX(),
                self.getPosY(),
                self.width,
                self.angle,
                'V' if self.visible else 'I',
                self.hjustify,
                self.vjustify,
                'I' if self.italic else 'N',
                'B' if self.bold else 'N'
                ))
