
import machine
import network

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False

# Other constants
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

def reset_cause():
    return machine.reset_cause()
    #raise NotImplementedError('reset_cause not implemented for this HW') 

def reset():
    machine.reset()
