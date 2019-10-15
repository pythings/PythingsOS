
#----------------------------
# System Abstraction Layer
#----------------------------
import os
import time
import machine
import network
import logger
import env
import stringstream

# The following can be overwritten or extended in the Hardware Abstraction Layer

class LED(object):
    @staticmethod
    def on():
        machine.Pin(2, machine.Pin.OUT).low()     
    @staticmethod
    def off():
        machine.Pin(2, machine.Pin.OUT).high()  

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
    
def get_tuuid():
    wlan = network.WLAN(network.STA_IF)
    mac_b = wlan.config('mac')
    mac_s = ':'.join( [ "%02X" % x for x in mac_b ] )
    return mac_s.replace(':','')

def get_reset_cause():
    return machine.reset_cause()

def reboot():
    machine.reset()
    time.sleep(3)

def is_frozen():
    import os
    try:
        os.stat(env.root+'/updates_pythings.py')
        return False
    except:
        return True


# The following are just platform-dependent, not hardware, and cannot be overwritten or extended.

def init():
    if logger.level > logger.DEBUG:
        logger.info('Disabling ESP os debug')
        import esp
        esp.osdebug(None)
    else:
        logger.info('Leaving ESP os debug enabled')

def get_payload_encrypter():  
    if is_frozen():
        try:
            from crypto_aes import Aes128ecb
            return Aes128ecb      
        except:
            return None
    else:
        return None

def get_mem_free():
    import gc
    return gc.mem_free()

def get_traceback(e):
    import uio
    import sys
    s = uio.StringIO()
    sys.print_exception(e, s)
    return s.getvalue() 

def get_re():
    import ure
    return ure

def socket_readline(s):
    return s.readline()

def socket_write(s,data):
    s.write(data)

def socket_ssl(s):
    import ussl
    return ussl.wrap_socket(s)

def execute(cmd):
    err = ''
    os.dupterm(stringstream)
    stringstream.clear()
    try:
        exec(cmd)
    except Exception as e:
        err = get_traceback(e)
    os.dupterm(None)
    return (stringstream.data + err)
