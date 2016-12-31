import logger
import sys
import time
import calendar
import ssl
import traceback

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False

# If set to True, disable payload encryption
HW_SUPPORTS_SSL        = False

# Frozen 
def is_frozen():
    return True

# Payload encryption (not needed if SSL support available)
def payload_encrypter():  
    if is_frozen():
        try:
            from crypto_aes import Aes128ecb
            return Aes128ecb      
        except:
            return None
    else:
        return None

# HW initializer (i.e. put PWMs to zero)
def init():
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

# Functions
def get_tuuid():
    raise NotImplementedError('I have no way to obtain an UUID for myself. You have to tell me my TID.')

def mem_free():
    return None

def get_traceback(e):
    return traceback.format_exc()

def reset_cause():
    raise NotImplementedError() 

def reboot():
    sys.exit(0)

# Filesystem (absolute) path
fspath = '/pythings_data'

# Regular expression are system-dependent
import re as re

# Time management is hardware-dependent
class Chronos(object):
    def __init__(self, epoch_s_now=0):
        pass
    def epoch(self):
        return calendar.timegm(time.gmtime())

# Socket readline, write and ssl wrapper are system-dependent
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

def socket_write(s,data):
    s.send(data)

def socket_ssl(s):
    return ssl.wrap_socket(s)#, ssl_version=ssl.PROTOCOL_TLSv1)
