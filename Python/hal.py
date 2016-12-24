import logger
import sys
import time
import calendar
import ssl




# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False

# You can set it to Ture, and disable payload encryption
HW_SUPPORTS_SSL        = False

# Payload encryption (not needed if SSL support available)
from crypto_aes import Aes128ecb
SW_PAYLOAD_ENCRYPTER    = Aes128ecb  

# HW initializer (i.e. put PWMs to zero)
def init():
    pass

payload_encrypter = Aes128ecb # PA

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

def is_os_frozen():
    return True

def mem_free():
    return None

def get_traceback(e):
    import traceback
    traceback.print_exc() # TODO: hetre

def reset_cause():
    raise NotImplementedError() 

def reboot():
    sys.exit(0)

# Filesystem (absolute) path
fspath = '/pydata'


# Regular expression are system-dependent
import re as re

# Time management is hardware-dependent
class Chronos(object):
    def __init__(self, epoch_s_now=0):
        pass
    def epoch_s(self):
        return calendar.timegm(time.gmtime())

# Socket readline and ssl wrapper are system-dependent
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
