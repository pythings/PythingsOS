import gc
import os
import sys
import json
import cache
gc.collect()

# Set root path
cache.root = '/'

print('')
try:
    try:
        with open(cache.root+'/settings.json','r') as f:
            pythings_version = json.loads(f.read())['pythings_version'] 
    except Exception as e:
        pythings_version = 'FACTORY'

    if not pythings_version.upper() == 'FACTORY':
        path = cache.root+'/'+pythings_version
        print('BOOT: Trying to load Pythings version {} from {}'.format(pythings_version,path))
        try:
            os.stat(path)
        except OSError:
            print('BOOT: Proceeding with factory default version...')
            path=cache.root
        else:
            try:
                os.stat(path+'/version.py')
            except OSError:
                print('BOOT: Error, proceeding with factory default version...')
                path=cache.root
            else:
                print('BOOT: OK, valid version {} found and loading...'.format(pythings_version))
                sys.path.insert(0, path)
    else:
        path=cache.root

except Exception as e:
    print('BOOT: Error, proceeding with factory defaults: ',e.__class.__.__name__, str(e))
    path=cache.root

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
    del cache

    

