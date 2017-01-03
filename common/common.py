import time
import logger
import sal

def run_controlled(retr, function, **kwargs):
    count=0
    while True:
        try:
            return function(**kwargs)   
        except Exception as e:
            print(sal.get_traceback(e))
            logger.error('Error in executing controlled step ({}): {} {}'.format(function,e.__class__.__name__,e))
            if retr == None or count < retr:
                count += 1
                logger.info('Retrying (#{}) in 3 seconds...'.format(count))
                time.sleep(3)
            else:
                logger.info('Exiting due to maximum retries reached')
                return
        finally:
            import gc
            gc.collect()

def get_app_version():
    try:
        from app import version as app_version
    except Exception as e:
        logger.info('Cannot obtain App version ({}:{}), falling back on version 0'.format(e.__class__.__name__, e))
        app_version='0'
    return app_version

def get_pythings_version():
    try:
        from version import version
    except Exception as e:
        logger.error('Error in obtaining Pythings version ({}: {}), skipping...'.format(e.__class__.__name__, e))
        version='Unknown'
    return version
