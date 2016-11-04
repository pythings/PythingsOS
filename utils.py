import os
import time
import globals
import network

def load_param(param, default=None):
    try:
        with open('/{}'.format(param),'r') as f:
            param = f.readline()
        return param
    except Exception as e:
        return default

def load_settings():
    import json
    settings = {}
    try:
        with open('/settings.json','r') as f:
            settings = json.loads(f.read())
    except Exception as e:
        print('Cannot open settings.py and load the json content: {}'.format(e))
    return settings

def mv(source,dest):
    try:
        import os
        try:
            os.remove(dest)
        except:
            pass
        os.rename(source, dest)
    except:
        pass

def get_tuuid():
    wlan = network.WLAN(network.STA_IF)
    mac_b = wlan.config('mac')
    mac_s = ':'.join( [ "%02X" % x for x in mac_b ] )
    return mac_s.replace(':','')