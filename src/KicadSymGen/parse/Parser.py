# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

import re

class Parser(object):
    '''
    Parser class is used to link device properties to symbols and signal
    properties from device to Units and Pins according to parsing rules
    '''

    def __init__(self, rules):
        '''
        Constructor

        Define default reg_ex base patterns, may be overwritten
        '''
        self.p_Name = "[a-zA-Z0-9_ /]+"
        self.p_ID = "\[(" + self.p_Name +")\]"
        self.p_DEV = "(DEV\[" + self.p_Name + "\])"
        self.p_SIG = "(SIG\[" + self.p_Name + "\])"
        '''
        Define values used by generator
        '''
        self.pinNameOffset = 40
        self.referenceField = None
        self.valueField = None
        self.footprintField = None
        self.datasheetField = None

        self.description = None
        self.keyWords = None
        self.docFileName = None

        self.rules = rules
        self.units = None

        '''
        Customize:
        '''
        self.pin_name = "SIG[PIN_NAME]"
        self.pin_number = "SIG[PIN_NUM]"

    def prepare(self):
        self.re_ID = re.compile(self.p_ID)
        self.re_DEV = re.compile(self.p_DEV)
        self.re_SIG = re.compile(self.p_SIG)

    def replace(self, old_text, dev, sig = None):
        '''
        Replace all tokens in str unsing properties from dev and sym
        '''
        tokens = self.re_DEV.findall(old_text)
        d = dev.getPropsDict()
        for dev_token in tokens:
            m = self.re_ID.search(dev_token)
            name = m.group(1)
            if name in d:
                v = d[name]
                old_text = old_text.replace(dev_token, v)
            else:
                raise NameError("Unknown device token: " + name)
        if sig:
            tokens = self.re_SIG.findall(old_text)
            d = sig.getPropsDict()
            for sig_token in tokens:
                m = self.re_ID.search(sig_token)
                name = m.group(1)
                if name in d:
                    v = d[name]
                    old_text = old_text.replace(sig_token, v)
                else:
                    raise NameError("Unknown signal token: " + name)
        return old_text

    def parse(self, dev):
        '''
        Parse next device using self.rules
        '''
        self.units = list(list())

    def getPinName(self, dev, sig):
        '''
        Returns device pin name
        '''
        pinName = self.replace(self.pin_name, dev, sig)
        return pinName

    def getPinNumber(self, dev, sig):
        '''
        Returns device pin name
        '''
        pinNumber = self.replace(self.pin_number, dev, sig)
        return pinNumber
