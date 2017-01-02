
#  Imports
import time
import gc
import globals
import common
import hal
import sal
from utils import load_param
from system import system

# Logger
import logger
logger.level = logger.DEBUG

# Utils
class EmptyResponse(Exception):
    pass

#---------------------
#  Main
#---------------------

def start():

    hal.init()

    # Get Pythings version
    globals.pythings_version = common.get_pythings_version()

    print('\n|------------------------|')
    print('|  Starting Pythings :)  |')
    print('|------------------------|')
    print('Version: {} ({})\n'.format(globals.pythings_version, system))
    import os

    try:
        os.stat(hal.get_fs_path())
    except:
        try:
            os.mkdir(hal.get_fs_path())
        except Exception as e:
            raise e from None

    import sys
    sys.path.append(hal.get_fs_path())
    
    if hal.HW_SUPPORTS_RESETCAUSE and hal.HW_SUPPORTS_WLAN:
        smt = load_param('smt', 60)
        # Start AP config mode if required
        if hal.get_reset_cause() == hal.HW_RESETCAUSE_HARD:
            if smt:
                gc.collect()
                if hal.HW_SUPPORTS_LED: hal.LED.on()
                from websetup import websetup
                websetup(timeout_s=smt, lock_session=True)
                if hal.HW_SUPPORTS_LED: hal.LED.off()
                # Reset (will start without AP config mode since this is a soft reset)
                logger.info('Resetting...')
                hal.reboot()

    # Disable AP mode, Enable and configure STA mode 
    if hal.HW_SUPPORTS_WLAN:
        hal.WLAN.ap_active(False)
        hal.WLAN.sta_active(True)

    # Start loading settings and parameters
    from utils import load_settings
    globals.settings = load_settings()
    globals.payload_encrypter = None # Initalization

    # Load backend: the local param worker_intervals 
    globals.backend = load_param('backend', None)

    # Load aid and tid: only local param or default
    globals.aid = load_param('aid', None)
    if globals.aid is None: raise Exception('AID not provided')
    globals.tid = load_param('tid', None)
    if globals.tid is None: globals.tid = hal.get_tuuid()

    if not globals.backend:
        backend_overrided = False
        if 'backend' in globals.settings and globals.settings['backend']:
            globals.backend = globals.settings['backend']
        else:
            globals.backend = 'backend.pythings.io'
    else:
        backend_overrided = True

    # Load pool: the local param worker_intervals 
    globals.pool = load_param('pool', None)
    if not globals.pool:
        if 'pool' in globals.settings and globals.settings['pool']:
            globals.pool = globals.settings['pool']
        else:
            globals.pool = 'production'
            
    globals.frozen = hal.is_frozen()

    # Tasks placeholders
    globals.app_worker_task = None
    globals.app_management_task = None
      
    # Report
    logger.info('Running with backend="{}" and aid="{}"'.format(globals.backend, globals.aid))

    # Get app version:    
    globals.app_version = common.get_app_version()
    gc.collect()

    # Register and perform the first management task call on "safe" backend, if not overrided
    if not backend_overrided:
        backend_set = globals.backend
        globals.backend ='backend.pythings.io'
    
    # Pre-register if payload encryption activated
    use_payload_encryption = globals.settings['payload_encryption'] if 'payload_encryption' in globals.settings else True
    if use_payload_encryption and hal.HW_SUPPORTS_ENCRYPTION and sal.get_payload_encrypter():
        logger.info('Enabling Payload Encryption and preregistering')
        globals.payload_encrypter = sal.get_payload_encrypter()(comp_mode=True)
        from register import preregister
        token = preregister()
        globals.token = token
        logger.info('Got token: {}'.format(globals.token))
        gc.collect()
        
    # Register yourself, and start a new session
    from register import register
    token, epoch = register()
    if not globals.payload_encrypter:
        globals.token = token
        logger.info('Got token: {}'.format(globals.token))
    gc.collect()
    
    # Sync time.
    chronos = hal.Chronos(epoch)

    # Call system management (will update App/Pythings versions  and settings if required)
    logger.info('Calling system management (preloop)')
    from management import system_management_task
    system_management_task(chronos)
    del system_management_task
    gc.collect()
    
    # Set back host to the proper one
    if not backend_overrided:
        globals.backend=backend_set
        del backend_set
    gc.collect()

    # Init app
    try:
        from worker_task import worker_task
        globals.app_worker_task = worker_task(chronos)
    except Exception as e:
        print(sal.get_traceback(e))
        from api import report
        logger.error('Error in importing/loading app\'s worker tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='worker', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, sal.get_traceback(e)))

    try:
        from management_task import management_task
        globals.app_management_task = management_task(chronos)
    except Exception as e:
        print(sal.get_traceback(e))
        from api import report
        logger.error('Error in importing/loading  app\'s management tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, sal.get_traceback(e)))

    # Setup intervals
    worker_interval = int(globals.settings['worker_interval']) if 'worker_interval' in globals.settings else 300
    management_interval = int(globals.settings['management_interval']) if 'management_interval' in globals.settings else 60

    # Start main loop
    loop_count = 0
    while True:
        
        if loop_count % management_interval == 0:
            logger.info('Calling management (loop={})'.format(loop_count))
            if hal.HW_SUPPORTS_LED:
                hal.LED.on(); time.sleep(0.05); hal.LED.off()
            from management import system_management_task
            system_management_task(chronos)
            del system_management_task
            gc.collect()
            logger.info('Done')

        if loop_count % worker_interval == 0:
            logger.info('Calling worker (loop={})'.format(loop_count))
            from worker import system_worker_task
            system_worker_task(chronos)
            del system_worker_task
            gc.collect()
            logger.info('Done')
            
        loop_count+=1
        time.sleep(1)


if __name__ == "__main__":
    start()

