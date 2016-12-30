import time
import logger
import hal

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

def get_app_version():
    try:
        from app import version as app_version
    except Exception as e:
        print(hal.get_traceback(e))
        logger.error('Error in importing version from app ({}:{}), trying obtaining it by parsing the file...'.format(e.__class__.__name__, str(e)))
        try:
            with open('/app.py','r') as file:
                last_line=None
                for line in file:
                    last_line=line
            app_version=last_line.split('=')[1].replace('\'','')
        except Exception as e:
            print(hal.get_traceback(e))
            logger.error('Error in reading version form app code ({}:{}), falling back on version 0: '.format(e.__class__.__name__, str(e)))
            app_version='0'
    return app_version

def get_pythings_version():
    try:
        from version import version
    except Exception as e:
        logger.error('Error in obtaining Pythings version: ({}: {}), skipping...'.format(e.__class__.__name__, str(e)))
        version='Unknown'
    return version
