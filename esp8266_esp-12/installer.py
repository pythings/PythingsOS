
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

# Generic calls
def apost(api, data={}):
    try:
        data['token'] = globals.token
    except AttributeError:
        pass             
    url = '{}/api/{}{}'.format(globals.pythings_host,version,api)
    logger.debug('Calling API {} with data'.format(url),data) 
    response = post(url, data=data)
    gc.collect()
    logger.debug('Got response:',response)
    if response['content'] :
        response['content'] = json.loads(response['content']) 
    logger.debug('Loaded json content and returning')
    return response

def report(what, status, message=None):
    logger.info('Reporting "{}" as "{}" with message "{}"'.format(what,status,message))
    response = apost('/things/report/', {'what':what,'status': status,'message': message})
    logger.debug('Response:',response)
''')
        f.write('''''')

    print('Writing',path+'/arch.py')
    with open(path+'/arch.py','w') as f:
        f.write('''arch = 'esp8266_esp-12'
''')
        f.write('''''')

    print('Writing',path+'/common.py')
    with open(path+'/common.py','w') as f:
        f.write('''import time
import logger

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
            import sys
            sys.print_exception(e)
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
        import sys
        sys.print_exception(e)
        logger.error('Error in importing version from app ({}:{}), trying obtaining it by parsing the file'.format(type(e), str(e)))
        try:
            with open('/app.py','r') as file:
                last_line=None
                for line in file:
                    last_line=line
            app_version=last_line.split('=')[1].replace('\\'','')
        except Exception as e:
            sys.print_exception(e)
            logger.error('Error in reading version form app code ({}:{}), falling back on version 0: '.format(type(e), str(e)))
            app_version='0'
    return app_version

def get_running_pythings_version():
    try:
        from version import version
    except Exception as e:
        logger.error('Error in obtaining Pythings version: ({}: {}), skipping...'.format(type(e), str(e)))
        version='Unknown'
    return version
''')
        f.write('''''')

    print('Writing',path+'/files.txt')
    with open(path+'/files.txt','w') as f:
        f.write('''file:880:api.py
file:24:arch.py
file:2257:common.py
file:419:files.txt
file:0:globals.py
file:964:hal.py
file:620:handle_main_error.py
file:3142:http.py
file:6579:init.py
file:35166:installer.pyc
file:662:logger.py
file:1370:main.py
file:3232:management.py
file:389:updates_app.py
file:1211:updates_pythings.py
file:682:updates_settings.py
file:1702:utils.py
file:7796:websetup.py
file:846:worker.py
file:15:version.py
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

# Constants (settings)
HW_SUPPORTS_DEEPSLEEP  = True
HW_SUPPORTS_RESETCAUSE = True
HW_SUPPORTS_LED        = True
HW_SUPPORTS_WLAN       = True

# Required if resetcause is supported
HARD_RESET = 6

def init():
    # i.e. turn off extra LEDs and lower PWMs
    pass

# Objects
class LED(object):
    @staticmethod
    def on():
        machine.Pin(2, machine.Pin.OUT).low()     
    @staticmethod
    def off():
        machine.Pin(2, machine.Pin.OUT).high() 

class WLAN(object):  
    @staticmethod
    def sta_active(mode):
        network.WLAN(network.STA_IF).active(mode)
    @staticmethod
    def ap_active(mode):
        network.WLAN(network.AP_IF).active(mode)

def get_tuuid():
    wlan = network.WLAN(network.STA_IF)
    mac_b = wlan.config('mac')
    mac_s = ':'.join( [ "%02X" % x for x in mac_b ] )
    return mac_s.replace(':','')

def reset_cause():
    return machine.reset_cause()

def reboot():
    machine.reset()
''')
        f.write('''''')

    print('Writing',path+'/handle_main_error.py')
    with open(path+'/handle_main_error.py','w') as f:
        f.write('''import sys
def handle(e):
    print('Error in executing Pythings framework: ',type(e), str(e))
    sys.print_exception(e)
    try:
        from api import report
        report('pythings', 'KO', e.__class__.__name__+' '+str(e))
    except Exception as e2:
        print('Error in reporting error to Pythings framework: ',type(e2), str(e2))
        sys.print_exception(e2) # TODO: try except also the prints as they can fail due to uncode   
    print('\\n{}: I will reset in 5 seconds. CTRL-C now to stop the reset.'.format(e.__class__.__name__)) 
    import time
    import machine
    time.sleep(5)
    machine.reset() ''')
        f.write('''''')

    print('Writing',path+'/http.py')
    with open(path+'/http.py','w') as f:
        f.write('''import socket
import json
import logger

# Note: post and get will load a single line to avoid memory problems in case of error 500
# pages and so on (Pythings backend will always provide responses in one line).

def post(url, data):

    _, _, host, path = url.split('/', 3)
    port=80
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    try: s.settimeout(60)
    except: pass
    s.connect(addr) #Tryexcept this
    s.write('%s /%s HTTP/1.0\\r\\nHost: %s\\r\\n' % ('POST', path, host))

    content = json.dumps(data)
    content_type = 'application/json'

    if content is not None:
        s.write('content-length: %s\\r\\n' % len(content))
        s.write('content-type: %s\\r\\n' % content_type)
        s.write('\\r\\n')
        s.write(content)
    else:
        s.write('\\r\\n')

    # Status, msg etc.
    version, status, msg = s.readline().split(None, 2)

    # Skip headers
    while s.readline() != b'\\r\\n':
        pass

    # Read data
    content = None
    while True:
        data = s.readline()
        if data:      
            content = str(data, 'utf8')
            break   
        else:
            break
        
    s.close()
    return {'version':version, 'status':status, 'msg':msg, 'content':content}
           

def get(url):
    _, _, host, path = url.split('/', 3)
    port=80
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
    version, status, msg = s.readline().split(None, 2)

    # Skip headers
    while s.readline() != b'\\r\\n':
        pass

    # Read data
    while True:
        data = s.readline
        if data:
            content = str(data, 'utf8')
        else:
            break
    s.close() #TODO: add a finally for closing the connnection?
    return {'version':version, 'status':status, 'msg':msg, 'content':content}


def download(source,dest):
    logger.info('Downloading {} in {}'.format(source,dest)) 
    f = open(dest, 'w')
    _, _, host, path = (source).split('/', 3)
    port=80
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
    version, status, msg = s.readline().split(None, 2)

    if status != b'200':
        logger.error('Status {} trying to get '.format(status),source)
        f.close()
        s.close()
        return False

    # Skip headers
    while s.readline() != b'\\r\\n': 
        pass 

    while True:
        data = s.readline() #data = s.rec''')
        f.write('''v(100)?
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
import machine
import time
import gc
import globals
import common
import hal
from utils import load_param

# Logger
import logger
logger.level = logger.DEBUG

#---------------------
#  Main
#---------------------

def start(path=None):

    # Get Pythings version
    globals.running_pythings_version = common.get_running_pythings_version()

    print('|------------------------|')
    print('|  Starting Pythings :)  |')
    print('|------------------------|')
    print('Version: {} (ESP8266)'.format(globals.running_pythings_version))

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
    globals.tid = load_param('tid', hal.get_tuuid())
    
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
    
    # Register yourself, and start a ne''')
        f.write('''w session
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
        logger.error('Error in importing/loading app\\'s worker tasks: {} {}'.format(e.__class__.__name__, e))
        common.run_controlled(2,report,what='worker', status='KO', message='{} {}'.format(e.__class__.__name__, e))

    try:
        from app import management_task
        globals.app_management_task = management_task(chronos)
    except Exception as e:
        import sys
        from api import report
        sys.print_exception(e)
        logger.error('Error in importing/loading  app\\'s management tasks: {} {}'.format(e.__class__.__name__, e))
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
from utils import load_settings
try:
    pythings_version = load_settings()['pythings_version']
    if not pythings_version.upper() == 'FACTORY':
        print('Trying to load Pythings version {}'.format(pythings_version))
        path = '/'+pythings_version
        try:
            os.stat(path)
        except OSError:
            print('No valid installation found for this version, proceeding with factory default version...')
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
    import sys
    sys.print_exception(e)
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

    # Update settings, pythings, app. TODO: move to try/except?
    try:
        if 'settings' in content['data'] and content['data']['settings'] != globals.settings:   
            from updates_settings import update_settings
            if update_settings(content): updates='settings' 
        
        elif globals.settings['pythings_version'].upper() != 'FACTORY' and globals.settings['pythings_version'] != globals.running_pythings_version:
            logger.debug('Downloading the new pythings (running version = "{}"; required version = "{}")'.format(globals.running_pythings_version, globals.settings['pythings_version']))
            from updates_pythings import update_pythings
            if update_pythings(globals.settings['pythings_version']): updates='pythings' 
 
        else:
            if globals.settings['app_version'] != globals.running_app_version:
                logger.debug('Downloading the new app (running version = "{}"; required version = "{}")'.format(globals.running_app_version, globals.settings['app_version']))
                from updates_app import update_app
                if update_app(globals.settings['app_version']): updates='app'  

    except Exception as e:
        import sys
        sys.print_exception(e)
        logger.error('Error in checking/updating {} ({}: {}), skipping the rest...'.format(updates,type(e), e))
        return False

    gc.collect()

    # If updates, reboot.
    if updates:
        logger.info('Rebooting due to update')
        run_controlled(2,report,what='pythings', status='OK', message='Resetting due to {} update'.format(updates))
        import hal
        hal.reboot()

    # Data = remote command sent, here we use a sample
    app_data     = content['data']['app_data'] if 'app_data' in content['data'] else None
    app_data_id  = content['data']['app_data_id'] if 'app_data_id' in content['data'] else None
    app_data_rep = None

    # Call App's management
    if globals.app_management_task:
        try:
            print('67----------------------------',gc.mem_free())
            app_data_rep=globals.app_management_task.call(chronos, app_data)
            if app_data_id:
                run_controlled(2,report,what='management', status='OK', message={'app_data_id':app_data_id,'app_data_rep':app_data_rep})
            else:
                run_controlled(2,report,what='management', status='OK')
                
        except Exception as e:
            import sys
            sys.print_excepti''')
        f.write('''on(e)
            logger.error('Error in executing app\\'s management task: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='management', status='KO', message='{} {}'.format(e.__class__.__name__, e))
''')

    print('Writing',path+'/updates_app.py')
    with open(path+'/updates_app.py','w') as f:
        f.write('''import globals
import logger
from utils import mv
from http import download

def update_app(version):
    try:
        mv('/app.py','/app_bk.py')
        if not download('{}/api/v1/apps/get/?version={}&token={}'.format(globals.pythings_host, version, globals.token), '/app.py'):  return False
        logger.info('Got new, updated app')
        return True
    except:
        return False''')
        f.write('''''')

    print('Writing',path+'/updates_pythings.py')
    with open(path+'/updates_pythings.py','w') as f:
        f.write('''
import globals
import logger
import os
from arch import arch

def update_pythings(version):
    source='http://backend.pythings.io/static/dist/PythingsOS/{}/{}'.format(version,arch)
    path='/'+version
    try:
        os.mkdir(path)
    except OSError as e:
        pass
    from http import download
    if not download(source+'/files.txt', path+'/files.txt'):
        return False
    files_list = open(path+'/files.txt')
    for item in files_list.read().split('\\n'):
        if 'file:' in item:
            filename=item.split(':')[2]
            if filename=='app.py': continue
            filesize=item.split(':')[1]
            download(source+'/'+filename, path+'/'+filename)
            if os.stat(path+'/'+filename)[6] != int(filesize):
                logger.error('Aborting: file expected size={}, actual size={}.'.format(filesize,os.stat(path+'/'+filename)[6]))
                os.remove(path+'/'+filename)
                files_list.close()
                return False
        else:
            if len(item)>0:
                logger.error('Aborting: Got unexpected format in files list.')
                files_list.close()
                return False
    files_list.close()
    return True
''')
        f.write('''''')

    print('Writing',path+'/updates_settings.py')
    with open(path+'/updates_settings.py','w') as f:
        f.write('''
import globals
import logger

def update_settings(content):
    try:
        logger.debug('Storing received settings ({} <--> {})'.format(content['data']['settings'], globals.settings))
        # TODO: Try load contents to validate?
        # Save backup for the settings file:
        from utils import mv
        mv('/settings.json','/settings_bk.json')
        # Ok, dump new settings
        f = open('/settings.json', 'w')
        import json
        f.write(json.dumps(content['data']['settings']))
        f.close()
        globals.settings = content['data']['settings']
        logger.info('Got new, updated settings')
        return True
    except:
        return False

''')
        f.write('''''')

    print('Writing',path+'/utils.py')
    with open(path+'/utils.py','w') as f:
        f.write('''import os
import ure

def connect_wifi(wlan, essid, password):
    print("Connecting with: ", essid)
    print("Using password: ", password)
    wlan.connect(essid, password)

def unquote(s):
    res = s.split('%')
    for i in range(1, len(res)): # no xrange as not available for this micro.
        item = res[i]
        try:
            res[i] = chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            res[i] = '%' + item
    return "".join(res)

def load_param(param, default=None):
    try:
        with open('/{}'.format(param),'r') as f:
            param = f.readline()
        return param
    except Exception as e:
        return default

def load_settings():
    import json
    settings = {}
    try:
        with open('/settings.json','r') as f:
            settings = json.loads(f.read())
    except Exception as e:
        print('Cannot open settings.py and load the json content: {}'.format(e))
    return settings

def mv(source,dest):
    try:
        import os
        try:
            os.remove(dest)
        except:
            pass
        os.rename(source, dest)
    except:
        pass



def get_wifi_data():
    try:
        with open('/wifi','r') as f:
            essid = f.readline()[0:-1]
            password = f.readline()
    except:
        essid=None
        password=None
    return (essid,password)

def parseURL(url):
    parameters = {}
    path = ure.search("(.*?)(\\?|$)", url).group(1)
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
        f.write('''version='v0.1'
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
from hal import get_tuuid

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
    ap.config(essid="Device_{}".format(get_tuuid()), authmode=network.AUTH_WPA_WPA2_PSK, password="NewDevice")
    
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
                if 'essid' in parameters: e''')
        f.write('''ssid = parameters['essid']   
                password = None
                if 'password' in parameters: password = parameters['password']                    
                try:
                    LED = machine.Pin(2, machine.Pin.OUT)  
                    LED.high()
                    time.sleep(0.3)
                    LED.low()
                except:
                    pass
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
from common import run_controlled

def system_worker_task(chronos):
    
    # Call App's worker    
    if globals.app_worker_task:
        app_data = None
        try:
            print('97----------------------------',gc.mem_free())
            app_data = globals.app_worker_task.call(chronos)
            if app_data:
                run_controlled(2,apost,api='/msg/drop/', data={'msg': app_data })
            report('worker','OK')
        except Exception as e:
            import sys
            sys.print_exception(e)
            logger.error('Error in executing app\\'s worker taks or sending its data: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='worker', status='KO', message='{} {}'.format(e.__class__.__name__, e))
            ''')
        f.write('''''')

    with open(path+'/initialized','w') as f:
        f.write('')

install()
            
    