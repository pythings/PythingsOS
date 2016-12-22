
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

    # Get Pythings version
    globals.running_pythings_version = common.get_running_pythings_version()

    print('\n|------------------------|')
    print('|  Starting Pythings :)  |')
    print('|------------------------|')
    print(' Version: {} ({})\n'.format(globals.running_pythings_version, arch))
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

    
    # Enable STA mode and Disable AP mode
    if hal.HW_SUPPORTS_WLAN:
        hal.WLAN.ap_active(False)
        hal.WLAN.sta_active(True)
    
    # Start loading settings and parameters
    from utils import load_settings
    globals.settings = load_settings()

    # Load aid and tid: only local param or default
    globals.aid = load_param('aid', None)
    if globals.aid is None: raise Exception('AID not provided')
    globals.tid = load_param('tid', None)
    if globals.tid is None: globals.tid = hal.get_tuuid()
    
    # Load backend_addr: the local param wins 
    globals.backend_addr = load_param('backend_addr', None)

    if not globals.backend_addr:
        backend_addr_overrided = False
        if 'backend_addr' in globals.settings and globals.settings['backend_addr']:
            globals.backend_addr = globals.settings['backend_addr']
        else:
            globals.backend_addr = 'backend.pythings.io'
    else:
        backend_addr_overrided = True

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
    logger.info('Running with backend_addr="{}" and aid="{}"'.format(globals.backend_addr, globals.aid))

    # Get app version:    
    globals.running_app_version = common.get_running_app_version()
    gc.collect()

    # Register and perform the first management task call on "safe" backend, if not overrided
    if not backend_addr_overrided:
        backend_addr_set = globals.backend_addr
        globals.backend_addr ='pythings.io'
    
    
    from api import apost
    
    # Activate paylpad encryption if any, and pre-register
    if hal.payload_encrypter:
        preregistered = True
        globals.token = None
        globals.payload_encrypter = hal.payload_encrypter(comp_mode=True)
        from crypto_rsa import Srsa
        pubkey = 28413003199647341169755148817272580434684756919496624803561225904937920874272008267922241718272669080997784342773848675977238304083346116914731539644572572184061626687258523348629880944116435872100013777281682624539900472318355160325153486782544158202452609602511838141993451856549399731403548343252478723563
        logger.info('Pre-registering myself with aes128cbc key="{}"'.format(globals.payload_encrypter.key))
        response = common.run_controlled(None,
                                         apost,
                                         api='/things/preregister/',
                                         data={'key': Srsa(pubkey).encrypt_text(str(globals.payload_encrypter.key)),
                                               'type': 'aes128cbc',
                                               'enc': 'srsa1'})
        
        if not response:
            raise EmptyResponse()

        # Set token
        globals.token = response['content']['data']['token']
        logger.info('Got token: {}'.format(globals.token))
 
    else:
        preregistered = False
        globals.payload_encrypter = None


    # Register yourself, and start a new session
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
        raise EmptyResponse()
    if not preregistered:
        globals.token = response['content']['data']['token']
        logger.info('Got token: {}'.format(globals.token))
    
    # Sync time.
    epoch_s = response['content']['data']['epoch_s']
    chronos = hal.Chronos(epoch_s)
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
    if not backend_addr_overrided:
        globals.backend_addr=backend_addr_set
        del backend_addr_set
    gc.collect()

    # Init app
    try:
        from app import worker_task
        globals.app_worker_task = worker_task(chronos)
    except Exception as e:
        import sys
        from api import report
        hal.print_exception(e)
        logger.error('Error in importing/loading app\'s worker tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='worker', status='KO', message='{} {}'.format(e.__class__.__name__, e))

    try:
        from app import management_task
        globals.app_management_task = management_task(chronos)
    except Exception as e:
        import sys
        from api import report
        hal.print_exception(e)
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
            if hal.HW_SUPPORTS_LED:
                hal.LED.on(); time.sleep(0.05); hal.LED.off()
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








