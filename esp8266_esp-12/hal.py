
import machine
import network

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = True
HW_SUPPORTS_RESETCAUSE = True
HW_SUPPORTS_LED        = True
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
        machine.Pin(2, machine.Pin.OUT).low()     
    @staticmethod
    def off():
        machine.Pin(2, machine.Pin.OUT).high() 

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

def reset_cause():
    return machine.reset_cause()

def reboot():
    machine.reset()
