import time
import logger
import hal

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
            print(hal.get_traceback(e))
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
        print(hal.get_traceback(e))
        logger.error('Error in importing version from app ({}:{}), trying obtaining it by parsing the file'.format(type(e), str(e)))
        try:
            with open('/app.py','r') as file:
                last_line=None
                for line in file:
                    last_line=line
            app_version=last_line.split('=')[1].replace('\'','')
        except Exception as e:
            print(hal.get_traceback(e))
            logger.error('Error in reading version form app code ({}:{}), falling back on version 0: '.format(type(e), str(e)))
            app_version='0'
    return app_version

def get_running_os_version():
    try:
        from version import version
    except Exception as e:
        logger.error('Error in obtaining Pythings version: ({}: {}), skipping...'.format(type(e), str(e)))
        version='Unknown'
    return version
