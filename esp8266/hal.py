
import machine
import network

import ure as re

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

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = True
HW_SUPPORTS_RESETCAUSE = True
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = True

# Required if resetcause is supported
HARD_RESET = 6

def init():
    # i.e. turn off extra LEDs and lower PWMs
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
        network.WLAN(network.STA_IF).active(mode)
    @staticmethod
    def ap_active(mode):
        network.WLAN(network.AP_IF).active(mode)

def get_tuuid():
    wlan = network.WLAN(network.STA_IF)
    mac_b = wlan.config('mac')
    mac_s = ':'.join( [ "%02X" % x for x in mac_b ] )
    return mac_s.replace(':','')

def is_os_frozen():
    import os
    try:
        os.stat('/initialized') # FSPATH!!!
        return False
    except:
        return True

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
