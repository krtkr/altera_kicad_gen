# -*- coding: utf-8 -*-
'''
Created on 8 июл. 2017 г.

@author: krtkr
'''

import bisect

def binary_search(self, a, x):  # can't use a to specify default for hi
    hi = len(a)
    pos = bisect.bisect_left(a, x, 0, hi)  # find insertion position
    return (pos if pos != hi and a[pos] == x else -1)  # don't walk off the end

def binary_del(self, a, x):  # can't use a to specify default for hi
    hi = len(a)
    pos = bisect.bisect_left(a, x, 0, hi)  # find insertion position
    if pos != hi and a[pos] == x:
        del a[pos]
    else:
        raise NameError('value is not there')

def binary_insert(self, a, x):
    hi = len(a)
    pos = bisect.bisect_left(a, x, 0, hi)  # find insertion position
    a.insert(pos, x)
