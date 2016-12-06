
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
    raise NotImplementedError()

def is_os_frozen():
    raise NotImplementedError() 

def mem_free():
    raise NotImplementedError() 

def get_traceback(e):
    raise NotImplementedError() 

def reset_cause():
    raise NotImplementedError() 

def reboot():
    sys.exit(0)
