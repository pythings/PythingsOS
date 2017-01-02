
#----------------------------
# System Abstraction Layer
#----------------------------

import sys
import time
import calendar
import ssl
import traceback


# The following can be overwritten or extended in the Hardware Abstraction Layer

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
    
class Chronos(object):
    def __init__(self, epoch_s_now=0):
        pass
    def epoch(self):
        return calendar.timegm(time.gmtime())
    
def is_frozen():
    return True

def get_tuuid():
    raise NotImplementedError('I have no way to obtain an UUID for myself. You have to tell me my TID.')

def get_reset_cause():
    raise NotImplementedError() 

def reboot():
    sys.exit(0)

def get_fs_path():
    from os.path import expanduser
    return(expanduser('~')+'/.pythings')


# The following are just system-dependent, not hardware, and cannot be overwritten or extended.

def init():
    pass

def get_payload_encrypter():
    try:
        from crypto_aes import Aes128ecb
        return Aes128ecb
    except:
        return None

def get_mem_free():
    return None

def get_traceback(e):
    return traceback.format_exc()

def get_re():
    import re
    return re

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