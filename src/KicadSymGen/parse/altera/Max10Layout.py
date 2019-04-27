'''
Created on 25 апр. 2019 г.

@author: krtkr
'''

from KicadSymGen.generate import Layout

class Max10Layout(Layout):
    '''
    This class cantains layout mapping of data read by Max10Reader to KiCAD
    symbols.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(Max10Layout, self).__init__()
        self.v_PinNameOffset = 20
        self.v_ReferenceField = "U"
        self.v_ValueField = "DEV[device_prefix]DEV[package_name]"
        self.v_FootprintField = "DEV[footprint]"
        self.v_DatasheetField = ""

        self.v_description = "DEV[description]"
        self.v_keyWords = "DEV[keyWords]"
        self.v_docFileName = "https://www.altera.com/content/dam/altera-www/global/en_US/pdfs/literature/hb/max-10/m10_handbook.pdf"
