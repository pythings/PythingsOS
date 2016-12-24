
# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False

# You can set it to True, and disable payload encryption
HW_SUPPORTS_SSL        = False

# Payload encryption (not needed if SSL support available)
SW_PAYLOAD_ENCRYPTER    = None 

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
    raise NotImplementedError()

# Filesystem (absolute) path
fspath = 'yourpath'

# Regular expression are system-dependent
import your_regex_module as re

# Time management is hardware-dependent
class Chronos(object):
    def __init__(self, epoch_s_now=0):
        raise NotImplementedError()
    def epoch_s(self):
        raise NotImplementedError()

# Socket readline and ssl wrapper are system-dependent
def socket_readline(s):
    raise NotImplementedError()

def socket_ssl(s):
    raise NotImplementedError()
