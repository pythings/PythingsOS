import logger
import sys
import time
import calendar
#import gc

# Regular expression are hardware-dependant
import re as re

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False

def init():
    # i.e. turn off extra LEDs and lower PWMs
    pass

# Objects
class LED(object):
    @staticmethod
    def on():
        raise NotImplementedError()  
    @staticmethod
    def off():
        raise NotImplementedError() 

class WLAN(object):  
    @staticmethod
    def sta_active(mode):
        raise NotImplementedError() 
    @staticmethod
    def ap_active(mode):
        raise NotImplementedError() 

def get_tuuid():
    raise NotImplementedError()

def reset_cause():
    raise NotImplementedError() 

def reboot():
    sys.exit(0)

# Print exception
def print_exception(e):
    import traceback
    traceback.print_exc()


def mem_free():
    return None
    #return gc.mem_free()

# Time management
class Chronos(object):
    def __init__(self, epoch_s_now=0):
        pass
    def epoch_s(self):
        return calendar.timegm(time.gmtime())

# Must be absolute
fspath = '/pydata'
    
def socket_readline(s):
    #data = s.makefile().readline()
    #logger.debug('Returning due to end of data=', data)
    #return data
    data=None
    prev_data_len=0
    end=False
    while True:
        if data is None:
            data = s.recv(1)
        else:
            data += s.recv(1)
        
        # TODO: This is weak, if source socket is still transmitting does not work. 
        if len(data) == prev_data_len:
            #logger.debug('Due to end of transmission returning data=', str(data, 'utf8'))
            if not end:
                return data
                end=True
            else:
                return None
        
        prev_data_len = len(data)

        if b'\n' in data:
            #logger.debug('Due to newline returning data=', str(data, 'utf8'))
            return data