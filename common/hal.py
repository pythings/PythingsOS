
import sys
 
# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False
HW_SUPPORTS_SSL        = False # You can set it to Ture, and disable payload encryption 


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

# Time management
class Chronos(object):
    def __init__(self, epoch_s_now=0):
        raise NotImplementedError()
    def epoch_s(self):
        raise NotImplementedError()

# Must be absolute
fspath = '/pydata'

# Socket-related
def socket_readline(s):
    raise NotImplementedError()

def socket_ssl(s):
    raise NotImplementedError()

