import logger
import sys
import time
import calendar
import ssl

# Regular expression are hardware-dependent
import re as re

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False
HW_SUPPORTS_SSL        = False # You can set it to Ture, and disable payload encryption 

def init():
    # i.e. turn off extra LEDs and lower PWMs. Not yet used
    pass

# Payload encryption (not needed if SSL support available)
from crypto_aes import Aes128cbc
payload_encrypter = Aes128cbc

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

# Socket-related
def socket_readline(s):
    data_tot = None
    data = s.recv(1)
    while data:
        if not data_tot:
            data_tot = data
        else:
            data_tot += data
        if b'\n' in data_tot:
            return data_tot
        data = s.recv(1)
    return data_tot

def socket_ssl(s):
    return ssl.wrap_socket(s)#, ssl_version=ssl.PROTOCOL_TLSv1)

