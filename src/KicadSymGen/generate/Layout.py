# -*- coding: utf-8 -*-
'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

import re

class Layout(object):
    '''
    Symbol layout kind. This class describe how pins should be distributed
    between Units, within Unit etc
    '''

    def __init__(self):
        '''
        Constructor

        Define default reg_ex base patterns, may be overwritten
        '''
        self.p_Name = "[a-zA-Z0-9_ ]+"
        self.p_ID = "\[(" + self.p_Name +")\]"
        self.p_DEV = "(DEV\[" + self.p_Name + "\])"
        self.p_SIG = "(SIG\[" + self.p_Name + "\])"
        '''
        Define values used by generator
        '''
        self.v_PinNameOffset = 40
        self.v_ReferenceField = None
        self.v_ValueField = None
        self.v_FootprintField = None
        self.v_DatasheetField = None

        self.v_description = None
        self.v_keyWords = None
        self.v_docFileName = None

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
                name = m.group()
                if name in d:
                    v = d[name]
                    old_text = old_text.replace(dev_token, v)
                else:
                    raise NameError("Unknown signal token: " + name)
        return old_text
