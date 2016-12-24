
import os

def install(path='/'):
    try:
        os.stat(path+'initialized')
        return
    except:
        pass

    print('Writing',path+'/api.py')
    with open(path+'/api.py','w') as f:
        f.write('''
import globals
import logger
import json
from http import post
import gc

version='v1'

def apost(api, data={}):
    try: token = globals.token
    except AttributeError: token=None
    if  globals.payload_encrypter and token:
        data =  {'encrypted': globals.payload_encrypter.encrypt_text(json.dumps(data))}
    if token: data['token'] = token
    url = '{}/api/{}{}'.format(globals.backend_addr,version,api)
    logger.debug('Calling API {} with data'.format(url),data)
    response = post(url, data=data)
    gc.collect()
    logger.debug('Got response:',response)
    if response['content'] and response['content'] != '\\n':
        response['content'] = json.loads(response['content']) 
    if globals.payload_encrypter:
        decrypted_data = globals.payload_encrypter.decrypt_text(response['content']['data'])
        response['content']['data'] = json.loads(decrypted_data)
    logger.debug('Loaded json content and returning')

    if response['status'] != b'200':
        raise Exception(response['content']['data'])
    return response

def report(what, status, message=None):
    logger.info('Reporting "{}" as "{}" with message "{}"'.format(what,status,message))
    response = apost('/things/report/', {'what':what,'status': status,'message': message})
    logger.debug('Response:',response)
''')
        f.write('''''')

    print('Writing',path+'/arch.py')
    with open(path+'/arch.py','w') as f:
        f.write('''arch = 'esp8266'
''')
        f.write('''''')

    print('Writing',path+'/common.py')
    with open(path+'/common.py','w') as f:
        f.write('''import time
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

def get_running_app_version():
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
            app_version=last_line.split('=')[1].replace('\\'','')
        except Exception as e:
            print(hal.get_traceback(e))
            logger.error('Error in reading version form app code ({}:{}), falling back on version 0: '.format(e.__class__.__name__, str(e)))
            app_version='0'
    return app_version

def get_running_os_version():
    try:
        from version import version
    except Exception as e:
        logger.error('Error in obtaining Pythings version: ({}: {}), skipping...'.format(e.__class__.__name__, str(e)))
        version='Unknown'
    return version
''')
        f.write('''''')

    print('Writing',path+'/files.txt')
    with open(path+'/files.txt','w') as f:
        f.write('''file:1314:api.py
file:17:arch.py
file:1788:common.py
file:397:files.txt
file:0:globals.py
file:2241:hal.py
file:764:handle_main_error.py
file:3828:http.py
file:6571:init.py
file:662:logger.py
file:1328:main.py
file:3365:management.py
file:1035:updates_app.py
file:1186:updates_pythings.py
file:603:updates_settings.py
file:1706:utils.py
file:7703:websetup.py
file:854:worker.py
file:19:version.py
''')
        f.write('''''')

    print('Writing',path+'/globals.py')
    with open(path+'/globals.py','w') as f:
        f.write('''''')
        f.write('''''')

    print('Writing',path+'/hal.py')
    with open(path+'/hal.py','w') as f:
        f.write('''
import machine
import network
import time

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = True
HW_SUPPORTS_RESETCAUSE = True
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = True

# If set to True, disable payload encryption
HW_SUPPORTS_SSL        = False

# Payload encryption (not needed if SSL support available)
from crypto_aes import Aes128ecb
SW_PAYLOAD_ENCRYPTER    = Aes128ecb 

# Required if RESETCAUSE is supported
HARD_RESET = 6

# HW initializer (i.e. put PWMs to zero)
def init():
    pass

# Objects
class LED(object):
    @staticmethod
    def on():
        pass     
    @staticmethod
    def off():
        pass 

class WLAN(object):  
    @staticmethod
    def sta_active(mode):
        network.WLAN(network.STA_IF).active(mode)
    @staticmethod
    def ap_active(mode):
        network.WLAN(network.AP_IF).active(mode)

# Functions
def get_tuuid():
    wlan = network.WLAN(network.STA_IF)
    mac_b = wlan.config('mac')
    mac_s = ':'.join( [ "%02X" % x for x in mac_b ] )
    return mac_s.replace(':','')

def is_os_frozen():
    import os
    try:
        os.stat(fspath+'/initialized')
        return False
    except:
        return True

def mem_free():
    import gc
    return gc.mem_free()

def get_traceback(e):
    import uio
    import sys
    s = uio.StringIO()
    sys.print_exception(e, s)
    return s.getvalue() 

def reset_cause():
    return machine.reset_cause()

def reboot():
    machine.reset()
    
# Filesystem (absolute) path
fspath = '/'

# Regular expression are system-dependent
import ure as re

# Time management is hardware-dependent
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

# Socket readline and ssl wrapper are system-dependent
def socket_readline(s):
    return s.readline()

def socket_ssl(s):
    raise NotImplementedError()


''')
        f.write('''''')

    print('Writing',path+'/handle_main_error.py')
    with open(path+'/handle_main_error.py','w') as f:
        f.write('''def handle(e):
    # Do not move the following import on top or code will fail (why?!)
    import hal
    print(hal.get_traceback(e))
    print('Error in executing Pythings framework: ',type(e), str(e))
    try:
        from api import report
        report(what='pythings', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))
    except Exception as e2:
        print('Error in reporting error to Pythings framework: ',type(e2), str(e2))
        print(hal.get_traceback(e2))
        # TODO: try except also the prints as they can fail due to uncode   
    print('\\n{}: I will reboot in 5 seconds. CTRL-C now to stop the reboot.'.format(e.__class__.__name__)) 
    import time
    time.sleep(5)
    import hal
    hal.reboot()
''')
        f.write('''''')

    print('Writing',path+'/http.py')
    with open(path+'/http.py','w') as f:
        f.write('''import socket
import json
import logger
import hal

# Note: post and get will load a single line to avoid memory problems in case of error 500
# pages and so on (Pythings backend will always provide responses in one line).

def post(url, data):
    port = 443 if hal.HW_SUPPORTS_SSL else 80 # TODO: port has to go after.
    url = 'https://'+url if hal.HW_SUPPORTS_SSL else 'http://'+url
    logger.info('Calling POST "{}" with data '.format(url),data)
    _, _, host, path = url.split('/', 3)
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    try: s.settimeout(60)
    except: pass

    if hal.HW_SUPPORTS_SSL:
        s = hal.socket_ssl(s)

    s.connect(addr) #TODO: Try-except this
    s.send(bytes('%s /%s HTTP/1.0\\r\\nHost: %s\\r\\n' % ('POST', path, host), 'utf8'))

    content = json.dumps(data)
    content_type = 'application/json'

    if content is not None:
        s.send(bytes('content-length: %s\\r\\n' % len(content), 'utf8'))
        s.send(bytes('content-type: %s\\r\\n' % content_type, 'utf8'))
        s.send(bytes('\\r\\n', 'utf8'))
        s.send(bytes(content, 'utf8'))
    else:
        s.send(bytes('\\r\\n', 'utf8'))

    # Status, msg etc.
    version, status, msg = hal.socket_readline(s).split(None, 2)

    # Skip headers
    while hal.socket_readline(s) != b'\\r\\n':
        pass

    # Read data
    content = None
    while True:
        data = hal.socket_readline(s)
        if data:      
            content = str(data, 'utf8')
            break   
        else:
            break
        
        
    s.close()
    return {'version':version, 'status':status, 'msg':msg, 'content':content}
           

def get(url):
    port = 443 if hal.HW_SUPPORTS_SSL else 80
    url = 'https://'+url if hal.HW_SUPPORTS_SSL else 'http://'+url
    logger.info('Calling GET "{}"'.format(url)) 
    _, _, host, path = url.split('/', 3)
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    try: s.settimeout(60)
    except: pass
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\\r\\nHost: %s\\r\\n\\r\\n' % (path, host), 'utf8'))

    # Status, msg etc.
    version, status, msg = hal.socket_readline(s).split(None, 2)

    # Skip headers
    while hal.socket_readline(s) != b'\\r\\n':
        pass

    # Read data
    while True:
        data = hal.socket_readline(s)
        if data:
            content = str(data, 'utf8')
        else:
            break
    s.close() #TODO: add a finally for closing the connnection?
    return {'version':version, 'status':status, 'msg':msg, 'content':content}


def download(source,dest):
    port = 443 if hal.HW_SUPPORTS_SSL else 80
    source = 'https://'+source if hal.HW_SUPPORTS_SSL else 'http://'+source
    logger.info('Downloading {} in {}'.format(source,dest)) 
    f = open(dest, 'w')
    _, _, host, path = (so''')
        f.write('''urce).split('/', 3)
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    try: s.settimeout(60)
    except: pass
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\\r\\nHost: %s\\r\\n\\r\\n' % (path, host), 'utf8'))
 
    # Status, msg etc.
    version, status, msg = hal.socket_readline(s).split(None, 2)

    if status != b'200':
        logger.error('Status {} trying to get '.format(status),source)
        f.close()
        s.close()
        return False

    # Skip headers
    while hal.socket_readline(s) != b'\\r\\n': 
        pass 

    while True:
        data = s.recv(100)
        if data:
            f.write((str(data, 'utf8')))
        else:
            break
    f.close()
    s.close()
    return True
''')

    print('Writing',path+'/init.py')
    with open(path+'/init.py','w') as f:
        f.write('''
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
    globals.running_os_version = common.get_running_os_version()

    print('\\n|------------------------|')
    print('|  Starting Pythings :)  |')
    print('|------------------------|')
    print(' Version: {} ({})\\n'.format(globals.running_os_version, arch))
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
    globals.payload_encrypter = None # Initalization

    # Load backend_addr: the local param wins 
    globals.backend_addr = load_param('backend_addr', None)

    # Load aid and tid: only local param or default
    globals.aid = load_param('aid', None)
    if globals.aid is None: raise Exception('AID not provided')
    globals.tid = load_param('tid', None)
    if globals.tid is None: globals.tid = hal.get_tuuid()

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
            
    globals.frozen_os = hal.is_os_frozen()

    # Tasks placeholders
    globals.app_worker_task = None
    globals.app_management_task = None
      
    # Report
    logger.info('Running with back''')
        f.write('''end_addr="{}" and aid="{}"'.format(globals.backend_addr, globals.aid))

    # Get app version:    
    globals.running_app_version = common.get_running_app_version()
    gc.collect()

    # Register and perform the first management task call on "safe" backend, if not overrided
    if not backend_addr_overrided:
        backend_addr_set = globals.backend_addr
        globals.backend_addr ='backend.pythings.io'
    
    # Pre-register if payload encryption activated
    if hal.SW_PAYLOAD_ENCRYPTER:
        globals.payload_encrypter = hal.SW_PAYLOAD_ENCRYPTER(comp_mode=True)
        from register import preregister
        token = preregister()
        globals.token = token
        logger.info('Got token: {}'.format(globals.token))
        gc.collect()
        
    # Register yourself, and start a new session
    from register import register
    token, epoch_s = register()
    if not globals.payload_encrypter:
        globals.token = token
        logger.info('Got token: {}'.format(globals.token))
    gc.collect()
    
    # Sync time.
    chronos = hal.Chronos(epoch_s)

    # Call system management (will update App/Pythings versions  and settings if required)
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
        from worker_task import worker_task
        globals.app_worker_task = worker_task(chronos)
    except Exception as e:
        print(hal.get_traceback(e))
        from api import report
        logger.error('Error in importing/loading app\\'s worker tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='worker', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))

    try:
        from management_task import management_task
        globals.app_management_task = management_task(chronos)
    except Exception as e:
        print(hal.get_traceback(e))
        from api import report
        logger.error('Error in importing/loading  app\\'s management tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))

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

''')

    print('Writing',path+'/logger.py')
    with open(path+'/logger.py','w') as f:
        f.write('''
DEBUG = 10
INFO = 20
WARNING =  30
ERROR = 40
CRITICAL= 50

level = INFO

def emit(level,msg, det):
        print('{}: '.format(level), end='')
        print(msg, end='')
        print(' ', end='')
        print(det, end='')
        print('')  

def debug(msg,det=''):
    if level <= DEBUG:
        emit('DEBUG',msg,det) 
  
def info(msg,det=''):
    if level <= INFO: 
        emit('INFO',msg,det) 
    
def warning(msg,det=''):
    if level <= WARNING: 
        emit('WARNING',msg,det) 

def error(msg,det=''):
    if level <= ERROR: 
        emit('ERROR',msg,det) 

def critical(msg,det=''):
    if level <= CRITICAL: 
        emit('CRITICAL',msg,det) 




''')
        f.write('''''')

    print('Writing',path+'/main.py')
    with open(path+'/main.py','w') as f:
        f.write('''import gc
import os
import sys

sys.path.append('/')
import hal
from utils import load_settings

try:
    pythings_version = load_settings()['pythings_version']
    if not pythings_version.upper() == 'FACTORY':
        print('Trying to load Pythings version {}'.format(pythings_version))
        path = '/'+pythings_version
        try:
            os.stat(path)
        except OSError:
            print('Proceeding with factory default version...')
            path='/'
        else:
            print('Updated version found, checking its consistency...')
            try:
                os.stat(path+'/version.py')
            except OSError:
                print('Error, proceeding with factory default version...')
                path='/'
            else:
                print('Valid updated version found.')
                sys.path.append(path)
                os.chdir(path)
    else:
        path='/'

except Exception as e:
    print (hal.get_traceback(e))
    print('Error, proceeding with factory defaults: ',type(e), str(e))
    path='/'

del load_settings

        
# Execute Pythings framework
try:
    import init
    gc.collect()
    init.start(path=path)

except Exception as e:
    import handle_main_error
    handle_main_error.handle(e) # Fallback on factory defaults?
finally:
    os.chdir('/')
    

''')
        f.write('''''')

    print('Writing',path+'/management.py')
    with open(path+'/management.py','w') as f:
        f.write('''import globals
import logger
from api import apost, report
import gc
from common import run_controlled
import hal

def system_management_task(chronos):
    
    updates=False
    
    # Call management API
    response = run_controlled(2,apost,api='/apps/management/')
    if response and 'content' in response: 
        content = response['content']
    else:
        logger.error('Error in receiving/parsing settings, skipping the rest of the management task!')
        return
    del response
    gc.collect()

    # Update settings, OS and App.
    try:
        if 'settings' in content['data'] and content['data']['settings'] != globals.settings:
            updates='settings'
            from updates_settings import update_settings
            update_settings(content)

        elif globals.settings['pythings_version'].upper() != 'FACTORY' and globals.settings['pythings_version'] != globals.running_os_version:
            updates='PythingsOS' 
            logger.debug('Downloading the new pythings (running version = "{}"; required version = "{}")'.format(globals.running_os_version, globals.settings['pythings_version']))
            from updates_pythings import update_pythings
            update_pythings(globals.settings['pythings_version'])

        else:
            if globals.settings['app_version'] != globals.running_app_version:
                updates='App' 
                logger.debug('Downloading the new app (running version = "{}"; required version = "{}")'.format(globals.running_app_version, globals.settings['app_version']))
                from updates_app import update_app
                update_app(globals.settings['app_version'])

    except Exception as e:
        print(hal.get_traceback(e))
        logger.error('Error in management task while updating {} ({}: {}), skipping the rest...'.format(updates, e.__class__.__name__, e))
        run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))
        return False

    gc.collect()

    # If updates, reboot.
    if updates:
        logger.info('Rebooting due to update')
        run_controlled(2,report,what='pythings', status='OK', message='Resetting due to {} update'.format(updates))
        hal.reboot()

    # Data = remote command sent, here we use a sample
    app_data     = content['data']['app_data'] if 'app_data' in content['data'] else None
    app_data_id  = content['data']['app_data_id'] if 'app_data_id' in content['data'] else None
    app_data_rep = None

    # Call App's management
    if globals.app_management_task:
        try:
            logger.debug('Mem free:', hal.mem_free())
            app_data_rep=globals.app_management_task.call(chronos, app_data)
            if app_data_id:
                run_controlled(2,report,what='management', status='OK', message={'app_data_id':app_data_id,'app_data_rep':app_data_rep})
            else:
                run_controlled(2,report,what='management', statu''')
        f.write('''s='OK')
                
        except Exception as e:
            import sys
            hal.get_traceback(e)
            logger.error('Error in executing app\\'s management task: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))
''')

    print('Writing',path+'/updates_app.py')
    with open(path+'/updates_app.py','w') as f:
        f.write('''import globals
import logger
from utils import mv
from api import apost
from http import download
from hal import fspath

def update_app(version):
    files = apost(api='/apps/get/', data={'version':version, 'list':True})['content']['data']
    # First of all remove /app.py to say that there is no valid App yet (download is in progress)
    import os
    try: os.remove(fspath+'/app.py')
    except: pass
    for file_name in files:
        if file_name in ['worker_task.py','management_task.py']:
            logger.info('Downloading "{}"'.format(file_name))
            if not download('{}/api/v1/apps/get/?file={}&version={}&token={}'.format(globals.backend_addr, file_name, version, globals.token), '{}/{}'.format(fspath, file_name)): 
                raise Exception('Error while donaloding')
        else:
            logger.info('NOT downloading "{}" as in forbidden list'.format(file_name))
    with open(fspath+'/app.py','w') as f:
        f.write('\\nversion=\\'{}\\''.format(version))
    logger.info('Got new, updated app')
''')
        f.write('''''')

    print('Writing',path+'/updates_pythings.py')
    with open(path+'/updates_pythings.py','w') as f:
        f.write('''
import globals
import logger
import os
from arch import arch
from hal import fspath

def update_pythings(version):
    source='http://backend.pythings.io/static/dist/PythingsOS/{}/{}'.format(version,arch)
    path=fspath+'/'+version
    try:
        os.mkdir(path)
    except OSError as e:
        pass
    from http import download
    if not download(source+'/files.txt', path+'/files.txt'):
        raise Exception('PythingsOS download failed')
    files_list = open(path+'/files.txt')
    for item in files_list.read().split('\\n'):
        if 'file:' in item:
            filename=item.split(':')[2]
            if filename=='app.py': continue
            filesize=item.split(':')[1]
            download(source+'/'+filename, path+'/'+filename)
            if os.stat(path+'/'+filename)[6] != int(filesize):
                os.remove(path+'/'+filename)
                files_list.close()
                raise Exception('File expected size={}, actual size={}.'.format(filesize,os.stat(path+'/'+filename)[6]))
        else:
            if len(item)>0:
                raise Exception('Got unexpected format in files list.')
                files_list.close()
    files_list.close()
''')
        f.write('''''')

    print('Writing',path+'/updates_settings.py')
    with open(path+'/updates_settings.py','w') as f:
        f.write('''
import globals
import logger
from hal import fspath

def update_settings(content):
    logger.debug('Storing received settings ({} <--> {})'.format(content['data']['settings'], globals.settings))
    # TODO: Try load contents to validate?
    # Save backup for the settings file:
    from utils import mv
    mv('/settings.json','/settings_bk.json')
    # Ok, dump new settings
    f = open(fspath+'/settings.json', 'w')
    import json
    f.write(json.dumps(content['data']['settings']))
    f.close()
    globals.settings = content['data']['settings']
    logger.info('Got new, updated settings')


''')
        f.write('''''')

    print('Writing',path+'/utils.py')
    with open(path+'/utils.py','w') as f:
        f.write('''import os
from hal import re, fspath

def connect_wifi(wlan, essid, password):
    print("Connecting with: ", essid)
    print("Using password: ", password)
    wlan.connect(essid, password)

def unquote(s):
    res = s.split('%')
    for i in range(1, len(res)):
        item = res[i]
        try:
            res[i] = chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            res[i] = '%' + item
    return "".join(res)

def load_param(param, default=None):
    try:
        with open(fspath+'/{}'.format(param),'r') as f:
            param = f.readline()
        return param
    except Exception as e:
        return default

def load_settings():
    import json
    settings = {}
    try:
        with open(fspath+'/settings.json','r') as f:
            settings = json.loads(f.read())
    except Exception as e:
        print('Cannot open settings.py and load the json content: {}'.format(e))
    return settings

def mv(source,dest):
    try:
        try:
            os.remove(fspath+'/'+dest)
        except:
            pass
        os.rename(fspath+'/'+source, fspath+'/'+dest)
    except:
        pass

def get_wifi_data():
    try:
        with open(fspath+'/wifi','r') as f:
            essid = f.readline()[0:-1]
            password = f.readline()
    except:
        essid=None
        password=None
    return (essid,password)

def parseURL(url):
    parameters = {}
    path = re.search("(.*?)(\\?|$)", url).group(1)
    if '?' in url:
        try:
            for keyvalue in url.split('?')[1].split('&'):
                parameters[unquote(keyvalue.split('=')[0])] = unquote(keyvalue.split('=')[1])
        except IndexError:
            pass
    return path, parameters
''')
        f.write('''''')

    print('Writing',path+'/version.py')
    with open(path+'/version.py','w') as f:
        f.write('''version='v0.2-pre'
''')
        f.write('''''')

    print('Writing',path+'/websetup.py')
    with open(path+'/websetup.py','w') as f:
        f.write('''
import network
import socket
import time
import machine
import logger
import json
import ure
import gc

from utils import *
import hal

def websetup(timeout_s=60, lock_session=False):
    logger.info('Starting WebSetup')
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(0)
    s.settimeout(timeout_s)
    logger.info('Listening on ', addr)
    CONF_PAGE_ACCESSED = False
    
    # Start AP mode and disable client mode
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="Device_{}".format(hal.get_tuuid()), authmode=network.AUTH_WPA_WPA2_PSK, password="NewDevice")
    
    while True:
        try:
            logger.info('Waiting for a connection..')
            gc.collect
            
            # Handle client connection
            cl, addr = s.accept()
            logger.info('Client connected from ', addr)
            if lock_session:
                s.settimeout(None)
            CONF_PAGE_ACCESSED = True

            # Read request
            request = str(cl.recv(1024))

            # Parse GET request
            get_request_data = ure.search("GET (.*?) HTTP\\/1\\.1", request)
            if get_request_data:
                path, parameters = parseURL(get_request_data.group(1))
                logger.debug('Got request for path = "{}" with params = "{}"'.format(path, parameters))
            else:
                path = []
                parameters = []

            cl.write('HTTP/1.0 200 OK\\r\\n')
            cl.write('Access-Control-Allow-Methods: POST, GET, OPTIONS\\r\\n');
            cl.write("Access-Control-Allow-Origin: *\\r\\n");
            #cl.write('Access-Control-Allow-Origin: http://localhost:8080\\n');
            cl.write("Access-Control-Allow-Credentials: true\\r\\n");
            cl.write("Access-Control-Allow-Headers: X-CSRFToken, ACCEPT, CONTENT-TYPE, X-CSRF-TOKEN, Content-Type, Authorization, X-Requested-With\\r\\n");

            if not get_request_data: # an OPTIONS, basically
                logger.debug('no GET data in request')
                cl.write('Content-Length: 0\\r\\n\\r\\n')
                cl.close()
                continue
            def set_api():
                cl.write('Content-Type: application/json\\r\\n')
                cl.write('\\r\\n')
            def set_page():
                cl.write('Content-Type: text/html\\r\\n')
                cl.write('\\r\\n')

            # Close connection if requesting favicon
            if 'favicon' in path:
                logger.debug('Requested favicon, closing connection')
                set_api()
                cl.close()
            
            # This is an API call
            elif 'cmd' in parameters:
                logger.debug('Called API with cmd={}'.format(parameters['cmd']))
                set_api()
                cmd = parameters['cmd']
                essid = None
                if 'essid' in parameters: essid = para''')
        f.write('''meters['essid']   
                password = None
                if 'password' in parameters: password = parameters['password']                    

                if hal.HW_SUPPORTS_LED:
                    hal.LED.off()
                    time.sleep(0.3)
                    hal.LED.on()

                gc.collect()

                # Set app command
                if cmd=='set_app':
                    logger.debug('Called set app API')
                    aid = None
                    aid = parameters['aid']
                    if aid is None:
                        cl.write(json.dumps({'status':'ERROR'}))
                    else:
                        with open('/aid','w') as f:
                            f.write(aid)
                    cl.write(json.dumps({'status':'OK', 'aid': load_param('aid',None)}))

                # Check command
                if cmd=='check':
                    import os
                    logger.debug('Called check API')
                    cl.write(json.dumps({'status':'OK', 'info': str(os.uname().version),'aid':load_param('aid',None)}))
                
                # Check_wifi command
                if cmd=='check_wifi':
                    logger.debug('Called check_wifi API')
                    sta.active(True)
                    essid='Unknown'
                    isconnected=False
                    essid,password = get_wifi_data()
                    if essid:
                        connect_wifi(sta, essid, password)
                        time.sleep(25)
                    isconnected = sta.isconnected()
                    sta.active(False) 
                    cl.write(json.dumps({'status':'OK', 'isconnected':isconnected, 'essid':essid}))
                
                # Scan command
                elif cmd == 'scan':
                    logger.debug('Called scan API')
                    sta.active(True)
                    nets = sta.scan() 
                    sta.active(False)
                    cl.write(json.dumps(nets))
                          
                # Join command                  
                elif cmd == 'join':
                    logger.debug('Called join API')
                    if password is None or essid is None:
                        cl.write(json.dumps({'status': 'ERROR'}))
                    else:
                        sta.active(True)
                        connect_wifi(sta, essid, password)
                        time.sleep(25)
                        isconnected = sta.isconnected()
                        saved = False
                        if isconnected:
                            try:
                                with open('/wifi','w') as f:
                                    f.write('{}\\n{}'.format(essid,password))
                                saved=True
                            except:
                                saved=False
                        sta.active(False)
                        cl.write(json.dumps({'status':'OK', 'isconnected':isconnected, 'essid':essid, 'saved':saved}))
                
                # Close command
                elif cmd == 'close':
                    logger.debug('Called close API')
                    cl.write(json.dumps({'status': 'OK'}))
                    cl.close()
                    s.close()
                    break

            #elif 'jquery' in path:
            #    logger.debug('Serving jquery')
            #    set_page()
            #    with open('/jquery.js') as f:
            #        for line in f:
            #            cl.write(line)

            else:
                logger.debug('Serving main page')
                set_page()
                cl.write('Please go to your vendor\\'s Website to configure this device.\\r\\n')
                #with open('websetup.html') as f:
                #    for line in f:
                #        cl.write(line)

            # Close client connection at the end
            logger.info('Closing client connection')
            cl.close()
        
        except OSError as e:
            if str(e) == "[Errno 110] ETIMEDOUT":
                if CONF_PAGE_ACCESSED:
                    #continue
                    logger.info('Exiting due to no activity')
                    s.close()
                    break
                
                else:
                    logger.info('Exiting due to no incoming connections')
                    s.close()
                    break
            import sys
            sys.print_exception(e)
            logger.error(str(e))
            try: cl.close()
            except: pass
            try: s.close()
            except: pass
            time.sleep(3)
''')

    print('Writing',path+'/worker.py')
    with open(path+'/worker.py','w') as f:
        f.write('''import globals
import logger
from api import apost, report
import gc
import hal
from common import run_controlled

def system_worker_task(chronos):
    
    # Call App's worker    
    if globals.app_worker_task:
        app_data = None
        try:
            logger.debug('Mem free:', hal.mem_free())
            app_data = globals.app_worker_task.call(chronos)
            if app_data:
                run_controlled(2,apost,api='/msg/drop/', data={'msg': app_data })
            report('worker','OK')
        except Exception as e:
            print(hal.get_traceback(e))
            logger.error('Error in executing app\\'s worker taks or sending its data: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='worker', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))
            ''')
        f.write('''''')

    with open(path+'/initialized','w') as f:
        f.write('')

install()
            
    