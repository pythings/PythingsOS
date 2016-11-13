import machine
import network
import ure
import socket
import time
import json
import globals
from http import post,get
import logger

def unquote(s):
    """Kindly rewritten by Damien from Micropython"""
    """No longer uses caching because of memory limitations"""
    res = s.split('%')
    for i in range(1, len(res)): # no xrange as not available for this micro.
        item = res[i]
        try:
            res[i] = chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            res[i] = '%' + item
    return "".join(res)

def connect_wifi(wlan, essid, password):
    print("Connecting with: ", essid)
    print("Using password: ", password) 
    wlan.connect(essid, password) # connect to an AP
    wlan.config('mac')      # get the interface's MAC adddress

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

def run_controlled(retr, function, **kwargs):
    count=0
    sleep=3
    while True:
        try:
            return function(**kwargs)   
        except Exception as e:
            import sys
            sys.print_exception(e)
            logger.error('Error in executing controlled step ({}): {} {}'.format(function,e.__class__.__name__,e))
            if retr == None or count < retr:
                count += 1
                logger.info('Retrying (#{}) in {} seconds...'.format(count,sleep))
                time.sleep(sleep)
            else:
                logger.info('Exiting due to maximum retries reached')
                return None
        finally:
            import gc
            gc.collect()

def get_running_app_version():
    try:
        from app import version as app_version
    except Exception as e:
        import sys
        sys.print_exception(e)
        logger.error('Error in importing version from app ({}:{}), trying obtaining it by parsing the file'.format(type(e), str(e)))
        try:
            with open('/app.py','r') as file:
                last_line=None
                for line in file:
                    last_line=line
            app_version=last_line.split('=')[1].replace('\'','')
        except Exception as e:
            sys.print_exception(e)
            logger.error('Error in reading version form app code ({}:{}), falling back on version 0: '.format(type(e), str(e)))
            app_version='0'
    return app_version

def get_running_pythings_version():
    try:
        f = open('version')
        version=f.read()
    except Exception as e:
        logger.error('Error in obtaining Pythings version: ',type(e), str(e), ', skipping...')    
        version='Unknown'
    finally:
        try: f.close()
        except:pass
    return version

