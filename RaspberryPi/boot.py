import gc
import os
import sys
import json
import env
gc.collect()

# Set root path
from os.path import expanduser
env.root = expanduser('~')+'/.pythings'

print('')
try:
    try:
        with open(env.root+'/settings.json','r') as f:
            pythings_version = json.loads(f.read())['pythings_version'] 
    except Exception as e:
        pythings_version = 'FACTORY'
    
    if not pythings_version.upper() == 'FACTORY':
        path = env.root+'/'+pythings_version
        print('BOOT: Trying to load Pythings version {} from {}'.format(pythings_version,path))
        try:
            os.stat(path)
        except OSError:
            print('BOOT: Proceeding with factory default version...')
            path=env.root
        else:
            try:
                os.stat(path+'/version.py')
            except OSError:
                print('BOOT: Error, proceeding with factory default version...')
                path=env.root
            else:
                print('BOOT: OK, valid version {} found and loading...'.format(pythings_version))
                sys.path.insert(0, path)
    else:
        path=env.root

except Exception as e:
    print('BOOT: Error, proceeding with factory defaults: ',e.__class.__.__name__, str(e))
    path=env.root

# Execute Pythings framework (from right path inserted above)
try:
    import init
    gc.collect()
    init.start()
except Exception as e:
    import handle_main_error
    handle_main_error.handle(e) 
    # TODO: Fallback on factory version?
finally:
    del env

    

