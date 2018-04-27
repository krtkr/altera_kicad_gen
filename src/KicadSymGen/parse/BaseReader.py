'''
Created on 23 апр. 2018 г.

@author: krtkr
'''

from abc import ABC, abstractmethod

class BaseReader(ABC):
    '''
    Abstract Reader: implement your specific reader using this base class
    '''

    @abstractmethod
    def nextDevice(self):
        """ Return next device if have any, Null is no more devices, return
        Device class instance here """
        return None
