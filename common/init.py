
#  Imports
import time
import gc
import globals
import common
import hal
from utils import load_param
from arch import arch

# Logger
import logger
logger.level = logger.DEBUG

# Utils
class EmptyResponse(Exception):
    pass

#---------------------
#  Main
#---------------------

def start(path=None):

    hal.init()

    # Get Pythings version
    globals.rpv = common.get_rpv()

    print('\n|------------------------|')
    print('|  Starting Pythings :)  |')
    print('|------------------------|')
    print(' Version: {} ({})\n'.format(globals.rpv, arch))
    import os

    try:
        os.stat(hal.fspath)
    except:
        try:
            os.mkdir(hal.fspath)
        except Exception as e:
            raise e from None

    import sys
    sys.path.append(hal.fspath)
    
    if hal.HW_SUPPORTS_RESETCAUSE and hal.HW_SUPPORTS_WLAN:
        websetup_timeout = load_param('websetup_timeout', 60)
        # Start AP config mode if required
        if hal.reset_cause() == hal.HARD_RESET:
            if websetup_timeout:
                gc.collect()
                if hal.HW_SUPPORTS_LED: hal.LED.on()
                from websetup import websetup
                websetup(timeout_s=websetup_timeout, lock_session=True)
                if hal.HW_SUPPORTS_LED: hal.LED.off()
                # Reset (will start without AP config mode since this is a soft reset)
                logger.info('Resetting...')
                hal.reboot()

    # Disable AP mode, Enable and configure STA mode 
    if hal.HW_SUPPORTS_WLAN:
        hal.WLAN.ap_active(False)
        hal.WLAN.sta_active(True)

    # Start loading stg and parameters
    from utils import load_stg
    globals.stg = load_stg()
    globals.payload_encrypter = None # Initalization

    # Load bea: the local param wins 
    globals.bea = load_param('bea', None)

    # Load aid and tid: only local param or default
    globals.aid = load_param('aid', None)
    if globals.aid is None: raise Exception('AID not provided')
    globals.tid = load_param('tid', None)
    if globals.tid is None: globals.tid = hal.get_tuuid()

    if not globals.bea:
        bea_overrided = False
        if 'bea' in globals.stg and globals.stg['bea']:
            globals.bea = globals.stg['bea']
        else:
            globals.bea = 'backend.pythings.io'
    else:
        bea_overrided = True

    # Load pln: the local param wins 
    globals.pln = load_param('pln', None)
    if not globals.pln:
        if 'pln' in globals.stg and globals.stg['pln']:
            globals.pln = globals.stg['pln']
        else:
            globals.pln = 'production'
            
    globals.fzp = hal.is_os_frozen()

    # Tasks placeholders
    globals.app_worker_task = None
    globals.app_management_task = None
      
    # Report
    logger.info('Running with bea="{}" and aid="{}"'.format(globals.bea, globals.aid))

    # Get app version:    
    globals.rav = common.get_rav()
    gc.collect()

    # Register and perform the first management task call on "safe" backend, if not overrided
    if not bea_overrided:
        bea_set = globals.bea
        globals.bea ='backend.pythings.io'
    
    # Pre-register if payload encryption activated
    use_pye = globals.stg['pye'] if 'pye' in globals.stg else True
    if hal.SW_PAYLOAD_ENCRYPTER and use_pye:
        logger.info('Enabling Payload Encryption and preregistering')
        globals.payload_encrypter = hal.SW_PAYLOAD_ENCRYPTER(comp_mode=True)
        from register import preregister
        tok = preregister()
        globals.tok = tok
        logger.info('Got tok: {}'.format(globals.tok))
        gc.collect()
        
    # Register yourself, and start a new session
    from register import register
    tok, eph = register()
    if not globals.payload_encrypter:
        globals.tok = tok
        logger.info('Got tok: {}'.format(globals.tok))
    gc.collect()
    
    # Sync time.
    chronos = hal.Chronos(eph)

    # Call system management (will update App/Pythings versions  and stg if required)
    logger.info('Calling system management (preloop)')
    from management import system_management_task
    system_management_task(chronos)
    del system_management_task
    gc.collect()
    
    # Set back host to the proper one
    if not bea_overrided:
        globals.bea=bea_set
        del bea_set
    gc.collect()

    # Init app
    try:
        from worker_task import worker_task
        globals.app_worker_task = worker_task(chronos)
    except Exception as e:
        print(hal.get_traceback(e))
        from api import report
        logger.error('Error in importing/loading app\'s worker tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='worker', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))

    try:
        from management_task import management_task
        globals.app_management_task = management_task(chronos)
    except Exception as e:
        print(hal.get_traceback(e))
        from api import report
        logger.error('Error in importing/loading  app\'s management tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))

    # Setup intervals
    worker_interval = int(globals.stg['worker_interval']) if 'worker_interval' in globals.stg else 300
    management_interval = int(globals.stg['management_interval']) if 'management_interval' in globals.stg else 60

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

