
#  Imports
import machine
import time
import gc
import network
import globals
import common
from utils import load_param

# Logger
import logger
logger.level = logger.DEBUG

#  Constants
LED = machine.Pin(2, machine.Pin.OUT)
HARD_RESET = 6

#---------------------
#  Main
#---------------------

def start():

    # Get Pythings version
    globals.running_pythings_version = common.get_running_pythings_version()

    print('|------------------------|')
    print('|  Starting Pythings :)  |')
    print('|------------------------|')
    print('Version: {} (ESP8266)'.format(globals.running_pythings_version))

    websetup_timeout = load_param('websetup_timeout', 60)
    # Start AP config mode if required
    if machine.reset_cause() == HARD_RESET:
        if websetup_timeout:
            gc.collect()
            LED.low()
            from websetup import websetup
            websetup(timeout_s=websetup_timeout, lock_session=True)
            LED.high()
            # Reset (will start without AP config mode since this is a soft reset)
            logger.info('Resetting...')
            machine.reset()

    # Enable STA mode and Disable AP mode
    network.WLAN(network.STA_IF).active(True)
    network.WLAN(network.AP_IF).active(False)

    # Start loading settings and parameters
    from utils import load_settings, get_tuuid
    globals.settings = load_settings()

    # Load aid and tid: only local param or default
    globals.aid = load_param('aid', None)
    globals.tid = load_param('tid', get_tuuid())
    
    # Load pythings_host: the local param wins 
    globals.pythings_host = load_param('pythings_host', None)
    if not globals.pythings_host:
        pythings_host_overrided = False
        if 'pythings_host' in globals.settings and globals.settings['pythings_host']:
            globals.pythings_host = 'http://'+globals.settings['pythings_host']
        else:
            globals.pythings_host = 'http://backend.pythings.io'
    else:
        pythings_host_overrided = True

    # Load pool: the local param wins 
    globals.pool = load_param('pool', None)
    if not globals.pool:
        if 'pool' in globals.settings and globals.settings['pool']:
            globals.pool = globals.settings['pool']
        else:
            globals.pool = 'production'

    # Tasks placeholders
    globals.app_worker_task = None
    globals.app_management_task = None
      
    # Report
    logger.info('Running with pythings_host="{}" and aid="{}"'.format(globals.pythings_host, globals.aid))

    # Get app version:    
    globals.running_app_version = common.get_running_app_version()
    gc.collect()

    # Register and perform the first management task call on "safe" backend
    if not pythings_host_overrided:
        pythings_host_set = globals.pythings_host
        globals.pythings_host ='http://backend.pythings.io'
    
    # Register yourself, and start a new session
    from api import apost
    logger.info('Registering myself with tid={} and aid={}'.format(globals.tid,globals.aid))
    response = common.run_controlled(None,
                                     apost,
                                     api='/things/register/',
                                     data={'tid':globals.tid,
                                           'aid': globals.aid,
                                           'running_app_version': globals.running_app_version,
                                           'running_pythings_version': globals.running_pythings_version,
                                           'pool': globals.pool,
                                           'settings': globals.settings})
    if not response:
        class EmptyResponse(Exception):
            pass
        raise EmptyResponse()
    
    globals.token = response['content']['data']['token']
    logger.info('Got token: {}'.format(globals.token))
    
    # Sync time.
    epoch_s = response['content']['data']['epoch_s']
    chronos = common.Chronos(epoch_s)
    del response
    gc.collect()

    # Call system management (will update App/Pythings versions  and settings if required)
    gc.collect()
    logger.info('Calling system management (preloop)')

    from management import system_management_task
    system_management_task(chronos)
    del system_management_task
    gc.collect()
    
    # Set back host to the proper one
    if not pythings_host_overrided:
        globals.pythings_host=pythings_host_set
        del pythings_host_set
    gc.collect()

    # Init app
    try:
        from app import worker_task
        globals.app_worker_task = worker_task(chronos)
    except Exception as e:
        import sys
        from api import report
        sys.print_exception(e)
        logger.error('Error in importing/loading app\'s worker tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='worker', status='KO', message='{} {}'.format(e.__class__.__name__, e))

    try:
        from app import management_task
        globals.app_management_task = management_task(chronos)
    except Exception as e:
        import sys
        from api import report
        sys.print_exception(e)
        logger.error('Error in importing/loading  app\'s management tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='worker', status='KO', message='{} {}'.format(e.__class__.__name__, e))

    # Setup intervals
    worker_interval = int(globals.settings['worker_interval']) if 'worker_interval' in globals.settings else 300
    management_interval = int(globals.settings['management_interval']) if 'management_interval' in globals.settings else 60

    # Start main loop
    loop_count = 0
    while True:
        
        if loop_count % management_interval == 0:
            logger.info('Calling management (loop={})'.format(loop_count))
            LED.low(); time.sleep(0.05); LED.high()
            from management import system_management_task
            system_management_task(chronos)
            del system_management_task
            gc.collect()

        if loop_count % worker_interval == 0:
            logger.info('Calling worker (loop={})'.format(loop_count))
            from worker import system_worker_task
            system_worker_task(chronos)
            del system_worker_task
            gc.collect()
            
        loop_count+=1
        time.sleep(1)


if __name__ == "__main__":
    start()








