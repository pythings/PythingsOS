
import machine
import network
import time

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = True
HW_SUPPORTS_RESETCAUSE = True
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = True

# If set to True, disable payload encryption
HW_SUPPORTS_SSL        = False

# Filesystem (absolute) path
fspath = '/'

def is_os_frozen():
    import os
    try:
        os.stat(fspath+'/initialized')
        return False
    except:
        return True

# Payload encryption (not needed if SSL support available)
if is_os_frozen():
    try:
        from crypto_aes import Aes128ecb
        SW_PAYLOAD_ENCRYPTER = Aes128ecb
    except:
        SW_PAYLOAD_ENCRYPTER = None
else:
    SW_PAYLOAD_ENCRYPTER = None

# Required if RESETCAUSE is supported
HARD_RESET = 6

# HW initializer (i.e. put PWMs to zero)
def init():
    pass

# Objects
class LED(object):
    @staticmethod
    def on():
        pass     
    @staticmethod
    def off():
        pass 

class WLAN(object):  
    @staticmethod
    def sta_active(mode):
        sta = network.WLAN(network.STA_IF)
        sta.active(mode)
        if mode is True:
            from utils import connect_wifi, get_wifi_data
            essid,password = get_wifi_data()
            if essid:
                connect_wifi(sta, essid, password)
    @staticmethod
    def ap_active(mode):
        network.WLAN(network.AP_IF).active(mode)

# Functions
def get_tuuid():
    wlan = network.WLAN(network.STA_IF)
    mac_b = wlan.config('mac')
    mac_s = ':'.join( [ "%02X" % x for x in mac_b ] )
    return mac_s.replace(':','')

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

# Regular expression are system-dependent
import ure as re

# Time management is hardware-dependent
class Chronos(object):
    def __init__(self, epoch_s_now=0):
        self.epoch_baseline_s    = epoch_s_now
        self.internal_baseline_s = int(time.ticks_ms()/1000)
    def epoch_s(self):
        if self.epoch_baseline_s is not None and self.internal_baseline_s is not None:
            current_epoch_ms = (int(time.ticks_ms()/1000) - self.internal_baseline_s) + self.epoch_baseline_s        
            return current_epoch_ms
        else:
            return time.ticks_ms()/1000

# Socket readline, write and ssl wrapper are system-dependent
def socket_readline(s):
    return s.readline()

def socket_write(s,data):
    s.write(data)

def socket_ssl(s):
    raise NotImplementedError()


