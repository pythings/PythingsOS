
#  Imports
from time import sleep
import gc
import cache
import common
import hal
import sal
from utils import load_param
from system import system

# Logger
import logger
logger.level = int(load_param('loglevel', logger.DEBUG))

# Start
def start():

    # Get Pythings version
    cache.pythings_version = common.get_pythings_version()

    print('\n|------------------------|')
    print('|  Starting Pythings :)  |')
    print('|------------------------|')
    print(' Version: {}'.format(cache.pythings_version))
    print(' System: {}\n'.format(system))

    # Init hardware and system
    hal.init()
    sal.init()
    
    # Start setup  mode if required
    if hal.HW_SUPPORTS_RESETCAUSE and hal.HW_SUPPORTS_WLAN and hal.get_reset_cause() in hal.HW_WEBSETUP_RESETCAUSES:
        setup_timeout = load_param('setup_timeout', 60)
        if setup_timeout:
            if hal.HW_SUPPORTS_LED: hal.LED.on()
            from websetup import websetup
            gc.collect()
            websetup(timeout_s=setup_timeout)
            if hal.HW_SUPPORTS_LED: hal.LED.off()
            logger.info('Resetting...')
            hal.reboot()

    # Disable AP mode, Enable and configure STA mode 
    if hal.HW_SUPPORTS_WLAN:
        hal.WLAN.ap_active(False)
        hal.WLAN.sta_active(True)

    # Start loading settings and parameters
    from utils import load_settings
    cache.settings = load_settings()
    cache.payload_encrypter = None # Initalization

    # Load backend: the local param wins 
    cache.backend = load_param('backend', None)

    if not cache.backend:
        backend_overrided = False
        if 'backend' in cache.settings and cache.settings['backend']:
            cache.backend = cache.settings['backend']
        else:
            cache.backend = 'backend.pythings.io'
    else:
        backend_overrided = True

    # Load aid and tid: only local param or default
    cache.aid = load_param('aid', None)
    if cache.aid is None:
        logger.critical('AID not provided, stopping here. Please set it up!')
        import time
        while True:
            time.sleep(1)
    cache.tid = load_param('tid', None)
    if cache.tid is None: cache.tid = hal.get_tuuid()

    # Load pool: the local param wins 
    cache.pool = load_param('pool', None)
    if not cache.pool:
        if 'pool' in cache.settings and cache.settings['pool']:
            cache.pool = cache.settings['pool']
        else:
            cache.pool = 'production'
            
    cache.frozen = hal.is_frozen()

    # Tasks placeholders
    cache.app_worker_task = None
    cache.app_management_task = None
      
    # Report
    logger.info('Running with backend="{}" and aid="{}"'.format(cache.backend, cache.aid))

    # Get app version:    
    cache.app_version = common.get_app_version()

    # Register and perform the first management task call on "safe" backend, if not overrided
    if not backend_overrided:
        backend_set = cache.backend
        cache.backend ='backend.pythings.io'
    
    # Pre-register if payload encryption activated
    use_payload_encryption = cache.settings['payload_encryption'] if 'payload_encryption' in cache.settings else True
    if use_payload_encryption and hal.HW_SUPPORTS_ENCRYPTION and sal.get_payload_encrypter():
        logger.info('Enabling Payload Encryption and preregistering')
        cache.payload_encrypter = sal.get_payload_encrypter()(comp_mode=True)
        from preregister import preregister
        token = preregister()
        cache.token = token
        logger.info('Got token: {}'.format(cache.token))
        del preregister
        gc.collect()
        
    # Register yourself, and start a new session
    from register import register
    token, epoch = register()
    if not cache.payload_encrypter:
        cache.token = token
        logger.info('Got token: {}'.format(cache.token))
    del register
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
        cache.backend=backend_set
        del backend_set
    gc.collect()

    # Init app
    try:
        from worker_task import worker_task
        cache.app_worker_task = worker_task(chronos)
    except Exception as e:
        logger.error('Error in importing/loading app\'s worker tasks: {} {}'.format(e.__class__.__name__, e))
        logger.debug(sal.get_traceback(e))
        from api import report
        common.run_controlled(2,report,what='worker', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, sal.get_traceback(e)))

    try:
        from management_task import management_task
        cache.app_management_task = management_task(chronos)
    except Exception as e:
        logger.error('Error in importing/loading  app\'s management tasks: {} {}'.format(e.__class__.__name__, e))
        logger.debug(sal.get_traceback(e))
        from api import report
        common.run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, sal.get_traceback(e)))

    # Setup intervals
    worker_interval = int(cache.settings['worker_interval']) if 'worker_interval' in cache.settings else 300
    management_interval = int(cache.settings['management_interval']) if 'management_interval' in cache.settings else 60

    # Start main loop
    loop_count = 0
    while True:
        
        if loop_count % management_interval == 0:
            logger.info('Calling management (loop={})'.format(loop_count))
            if hal.HW_SUPPORTS_LED:
                hal.LED.on(); sleep(0.05); hal.LED.off()
            from management import system_management_task
            system_management_task(chronos)
            del system_management_task
            gc.collect()
            logger.info('Done management')

        if loop_count % worker_interval == 0:
            logger.info('Calling worker (loop={})'.format(loop_count))
            from worker import system_worker_task
            system_worker_task(chronos)
            del system_worker_task
            gc.collect()
            logger.info('Done worker')
            
        loop_count+=1
        sleep(1)


if __name__ == "__main__":
    start()

