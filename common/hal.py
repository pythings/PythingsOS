
import sys

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False

def init():
    # i.e. turn off extra LEDs and lower PWMs
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

def get_tuuid():
    return '000000000001'

def reset_cause():
    raise NotImplementedError() 

def reboot():
    sys.exit(0)
