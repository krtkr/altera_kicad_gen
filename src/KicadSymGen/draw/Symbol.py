# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

from KicadSymGen.draw import Field
from KicadSymGen.draw import Pin
from KicadSymGen.draw import Rectangle

import datetime

class Alias(object):
    '''
    KiCAD library Alias
    '''

    def __init__(self, name):
        '''
        Constructor
        '''
        self.name = name
        self.description = ""
        self.keyWords = ""
        self.docFileName = ""

class Symbol(object):
    '''
    KiCAD symbol - main unit for generation

    Parameters according to KiCAD's source code:
    int                 m_pinNameOffset;    ///< The offset in mils to draw the pin name.  Set to 0
                                            ///< to draw the pin name above the pin.
    bool                m_unitsLocked;      ///< True if part has multiple units and changing
                                            ///< one unit does not automatically change another unit.
    bool                m_showPinNames;     ///< Determines if part pin names are visible.
    bool                m_showPinNumbers;   ///< Determines if part pin numbers are visible.
    timestamp_t         m_dateLastEdition;  ///< Date of the last modification.
    LIBRENTRYOPTIONS    m_options;          ///< Special part features such as POWER or NORMAL.)
    int                 m_unitCount;        ///< Number of units (parts) per package.
    LIB_ITEMS_CONTAINER m_drawings;         ///< Drawing items of this part.
    wxArrayString       m_FootprintList;    /**< List of suitable footprint names for the
                                                 part (wild card names accepted). */
    LIB_ALIASES         m_aliases;          ///< List of alias object pointers associated with the
                                            ///< part.
    '''

    OPTION_NORMAL = 1
    OPTION_POWER = 2

    def __init__(self, name):
        '''
        Constructor
        '''
        self.pinNameOffset = 40
        self.unitsLocked = False
        self.showPinNames = True
        self.showPinNumbers = True
        self.dateLastEdition = datetime.datetime.now()
        self.options = Symbol.OPTION_NORMAL
        self.unitCount = 1
        self.drawings = list()
        self.footprintList = list()
        self.aliases = list()
        self.aliases.append(Alias(name))
        self.fields = list()
        self.fields.append(Field(Field.REFERENCE))
        self.fields.append(Field(Field.VALUE))
        self.fields.append(Field(Field.FOOTPRINT))
        self.fields.append(Field(Field.DATASHEET))

    def setDescription(self, description):
        self.aliases[0].description = description

    def setKeyWords(self, keyWords):
        self.aliases[0].keyWords = keyWords

    def setDocFileName(self, docFileName):
        self.aliases[0].docFileName = docFileName

    def addAlias(self, name, description, keyWords, docFileName):
        new_alias = Alias(name)
        new_alias.description = description
        new_alias.keyWords = keyWords
        new_alias.docFileName = docFileName
        self.aliases.append(new_alias)

    def referenceField(self):
        return self.fields[Field.Field.REFERENCE]

    def valueField(self):
        return self.fields[Field.Field.VALUE]

    def footprintField(self):
        return self.fields[Field.Field.FOOTPRINT]

    def datasheetField(self):
        return self.fields[Field.Field.DATASHEET]

    def addDrawing(self, drawing):
        self.drawings.append(drawing)

    def addPin(self, number, name):
        new_pin = Pin.Pin(number, name)
        self.drawings.append(new_pin)
        return new_pin

    def addRectangle(self):
        new_rect = Rectangle.Rectangle()
        self.drawings.append(new_rect)
        return new_rect
    
    def isPower(self):
        return self.options == Symbol.OPTION_POWER

    def write(self, writer):
        writer.writeLib("#\n# {:s}\n#\n".format(self.aliases[0].name))
        writer.writeLib("DEF {:s}".format(self.aliases[0].name))
        
        if self.referenceField().value:
            writer.writeLib(" {:s}".format(self.referenceField().value))
        else:
            writer.writeLib(" ~")

        writer.writerLib(" {:d} {:d} {:s} {:s} {:d} {:s} {:s}\n".format(
            0,
            self.pinNameOffset,
            'Y' if self.showPinNumbers else 'N',
            'Y' if self.showPinNames else 'N',
            self.unitCount,
            'L' if self.unitsLocked else 'N',
            'P' if self.isPower() else 'N'
            ))

        for idx, field in enumerate(self.fields):
            '''
            There is no need to save empty fields, i.e. no reason to preserve field
            names now that fields names come in dynamically through the template
            fieldnames.
            '''
            if field.value:
                field.write(writer)

        '''
        Save the alias list: a line starting by "ALIAS".  The first alias is the root
        and has the same name as the component.  In the old library file format this
        alias does not get added to the alias list.
        '''
        if len(self.aliases) > 1:
            writer.writeLib("ALIAS");
            for idx, alias in enumerate(self.aliases):
                if (idx == 0):
                    continue
                writer.writeLib(" {:s}".format(alias.name))
            writer.writeLib("\n");

        if self.footprintList:
            writer.writeLib("$FPLIST\n");
            for footprint in self.footprintList:
                writer.writeLib(" {:s}\n".format(footprint))
            writer.writeLib("$ENDFPLIST\n");
        
        if self.drawings:
            writer.writeLib("DRAW\n");
            for drawing in self.drawings:
                drawing.write(writer)
            writer.writeLib("ENDDRAW\n");

        writer.writeLib("ENDDEF\n");

        for alias in self.aliases:
            writer.writeDcm('$CMP ' + alias.name.upper() + '\n')
            writer.writeDcm('D ' + alias.description + '\n')
            writer.writeDcm('K ' + alias.keyWords + '\n')
            writer.writeDcm('F ' + alias.docFileName + '\n')
            writer.writeDcm('$ENDCMP\n')
            writer.writeDcm('#\n')
