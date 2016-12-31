
import machine
import time

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False

# If set to True, disable payload encryption
HW_SUPPORTS_SSL        = False

# Frozen
def is_frozen():
    return False
def is_os_frozen():
    return is_frozen()

# Payload encryption (not needed if SSL support available)
def payload_encrypter():  
    try:
        from crypto_aes import Aes128ecb
        return Aes128ecb
    except:
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
    import gc
    return gc.mem_free()

def get_traceback(e):
    import uio
    import sys
    s = uio.StringIO()
    sys.print_exception(e, s)
    return s.getvalue() 

def reset_cause():
    return machine.reset_cause()

def reboot():
    machine.reset()

# Filesystem (absolute) path
fspath = '/pythings_data'

# Regular expression are system-dependent
import ure as re

# Time management is hardware-dependent
class Chronos(object):
    def __init__(self, epoch_s_now=0):
        self.epoch_baseline_s    = epoch_s_now
        self.internal_baseline_s = int(time.ticks_ms()/1000)
    def epoch(self):
        if self.epoch_baseline_s is not None and self.internal_baseline_s is not None:
            current_epoch_s = (int(time.ticks_ms()/1000) - self.internal_baseline_s) + self.epoch_baseline_s        
            return current_epoch_s
        else:
            return time.ticks_ms()/1000

# Socket readline, write and ssl wrapper are system-dependent
def socket_readline(s):
    return s.readline()

def socket_write(s,data):
    s.write(data)

def socket_ssl(s):
    import ussl
    return ussl.wrap_socket(s)
