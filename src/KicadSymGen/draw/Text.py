# -*- coding: utf-8 -*-
'''
Created on 19 авг. 2019 г.

@author: krtkr
'''

from KicadSymGen.draw.DrawItem import DrawItem

class Text(DrawItem):
    '''
    KiCAD Symbol library draw item: text
    '''

    HJUSTIFY_CENTER = 'C'
    HJUSTIFY_LEFT = 'L'
    HJUSTIFY_RIGHT = 'R'

    VJUSTIFY_CENTER = 'C'
    VJUSTIFY_BOTTOM = 'B'
    VJUSTIFY_TOP = 'T'

    def __init__(self, unit = 0):
        super(Text, self).__init__(unit)
        self.angle = 0
        self.position = [0, 0]
        self.width = 50
        ''' visible is inverted! '''
        self.visible = 0
        self.text = ""
        self.italic = "Normal"
        self.bold = 0
        self.hjustify = Text.HJUSTIFY_CENTER
        self.vjustify = Text.VJUSTIFY_CENTER

    def setPos(self, x, y):
        self.position[0] = x
        self.position[1] = y

    def getPosX(self):
        return self.position[0]

    def getPosY(self):
        return self.position[1]

    def setVisible(self, visible):
        if visible:
            self.visible = 0
        else:
            self.visible = 1

    def setBold(self, bold):
        if bold:
            self.bold = 1
        else:
            self.bold = 0

    def setItalic(self, italic):
        if italic:
            self.italic = "Italic"
        else:
            self.italic = "Normal"

    def setText(self, text):
        self.text = text

    def write(self, writer):
        writer.writeLib(
            "T {:d} {:d} {:d} {:d} {:d} {:d} {:d} \"{:s}\" {:s} {:d} {:s} {:s}\n".format(
            self.angle,
            self.getPosX(),
            self.getPosY(),
            self.width,
            self.visible,
            self.unit,
            self.convert,
            self.text,
            self.italic,
            self.bold,
            self.hjustify,
            self.vjustify)
        )
