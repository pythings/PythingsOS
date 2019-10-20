
#----------------------------
# System Abstraction Layer
#----------------------------
import os
import uos
import uio
import sys
import time
import machine
import env
import usocket as socket

# The following can be overwritten or extended in the Hardware Abstraction Layer

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
    
def is_frozen():
    return False

def get_tuuid():
    raise NotImplementedError('I have no way to obtain an UUID for myself. You have to tell me my TID.')

def get_reset_cause():
    return machine.reset_cause()

def reboot():
    sys.exit()


# The following are just platform-dependent, not hardware, and cannot be overwritten or extended.

def init():
        
    # Create root path if not existent
    try:
        os.stat(env.root)
    except:
        try:
            os.mkdir(env.root)
        except Exception as e:
            raise e from None
        
    # Append root to the sys path
    sys.path.append(env.root)

def get_payload_encrypter():
    try:
        from crypto_aes import Aes128ecb
        return Aes128ecb
    except:
        return None

def get_mem_free():
    import gc
    return gc.mem_free()

def get_traceback(e):
    import sys
    s = uio.StringIO()
    sys.print_exception(e, s)
    return s.getvalue() 

def get_re():
    import ure
    return ure

def socket_read(s, n):
    try: return s.read(n)
    except AttributeError: return s.recv(n)

def socket_readline(s):
    return s.readline()

def socket_write(s,data):
    s.write(data)

def socket_ssl(s):
    import ussl
    return ussl.wrap_socket(s)

def execute(cmd):
    mystdout = uio.StringIO()
    err = ''
    uos.dupterm(mystdout, 1)
    try:
        exec(cmd)
    except Exception as e:
        err = get_traceback(e)
    uos.dupterm(None)
    return (mystdout.getvalue() + err)









