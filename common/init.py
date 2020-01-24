
#  Imports
from time import sleep
import gc
import env
import common
import hal
import pal
from utils import load_param
from platform import platform

# Logger
import logger
logger.level = int(load_param('loglevel', logger.INFO ))

# Start
def start():

    # Get Pythings version
    env.pythings_version = common.get_pythings_version()

    print('\n|--------------------------|')
    print('|  Starting PythingsOS :)  |')
    print('|--------------------------|')
    print(' Version: {}'.format(env.pythings_version))
    print(' Platform: {}'.format(platform))
    try: print(' Thing ID: {}\n'.format(hal.get_tid()))
    except: pass

    # Init hardware and platform
    hal.init()
    pal.init()
    
    # Start setup  mode if required
    if hal.HW_SUPPORTS_RESETCAUSE and hal.HW_SUPPORTS_WLAN and hal.get_reset_cause() in hal.WEBSETUP_RESETCAUSES:
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
    env.settings = load_settings()
    env.payload_encrypter = None # Initalization

    # Load backend: the local param wins 
    env.backend = load_param('backend', None)

    if not env.backend:
        backend_overrided = False
        if 'backend' in env.settings and env.settings['backend']:
            env.backend = env.settings['backend']
        else:
            env.backend = 'backend.pythings.io'
    else:
        backend_overrided = True

    # Load aid and tid: only local param or default
    env.aid = load_param('aid', None)
    if env.aid is None:
        logger.critical('AID not provided, stopping here. Please set it up!')
        import time
        while True:
            time.sleep(1)
    env.tid = load_param('tid', None)
    if env.tid is None: env.tid = hal.get_tid()

    # Load pool: the local param wins 
    env.pool = load_param('pool', None)
    if not env.pool:
        if 'pool' in env.settings and env.settings['pool']:
            env.pool = env.settings['pool']
        else:
            env.pool = 'production'
            
    env.frozen = hal.is_frozen()

    # Tasks placeholders
    env.app_workerTask = None
    env.app_managementTask = None
      
    # Report
    logger.info('Running with backend="{}" and aid="{}"'.format(env.backend, env.aid))

    # Get app version:
    env.app_version = common.get_app_version()

    # Register and perform the first management task call on "safe" backend, if not overrided
    if not backend_overrided:
        backend_set = env.backend
        env.backend ='backend.pythings.io'
    
    # Pre-register if payload encryption activated
    use_payload_encryption = env.settings['payload_encryption'] if 'payload_encryption' in env.settings else hal.USE_ENCRYPTION_DEFAULT
    if use_payload_encryption and hal.HW_SUPPORTS_ENCRYPTION and pal.get_payload_encrypter():
        logger.info('Enabling Payload Encryption and preregistering')
        env.payload_encrypter = pal.get_payload_encrypter()(comp_mode=True)
        from preregister import preregister
        token = preregister()
        env.token = token
        logger.info('Got token: {}'.format(env.token))
        del preregister
        gc.collect()
        
    # Register yourself, and start a new session
    from register import register
    token, epoch = register()
    if not env.payload_encrypter:
        env.token = token
        logger.info('Got token: {}'.format(env.token))
    del register
    gc.collect()
    
    # Sync time and add to env
    chronos = hal.Chronos(epoch)
    env.chronos = chronos

    # Call system management (will update App/Pythings versions  and settings if required)
    logger.info('Calling system management (preloop)')
    from management import system_management_task
    system_management_task(chronos)
    del system_management_task
    gc.collect()
    
    # Set back host to the proper one
    if not backend_overrided:
        env.backend=backend_set
        del backend_set
    gc.collect()

    # Init app
    try:
        from worker_task import WorkerTask
        env.app_workerTask = WorkerTask()
    except Exception as e:
        logger.error('Error in importing/loading app\'s worker tasks: {} {}'.format(e.__class__.__name__, e))
        logger.debug(pal.get_traceback(e))
        from api import report
        common.run_controlled(2,report,what='worker', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, pal.get_traceback(e)))

    try:
        from management_task import ManagementTask
        env.app_managementTask = ManagementTask()
    except Exception as e:
        logger.error('Error in importing/loading  app\'s management tasks: {} {}'.format(e.__class__.__name__, e))
        logger.debug(pal.get_traceback(e))
        from api import report
        common.run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, pal.get_traceback(e)))

    # Setup intervals
    worker_interval = int(env.settings['worker_interval']) if 'worker_interval' in env.settings else 300
    management_interval = int(env.settings['management_interval']) if 'management_interval' in env.settings else 60

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

