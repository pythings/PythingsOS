import gc
import os
import sys
import json
import hal

# TODO: not sure if we need it anymore
#sys.path.append('/')

fs_path= hal.get_fs_path()
try:
    try:
        with open(fs_path+'/settings.json','r') as f:
            settings = json.loads(f.read())
    except Exception as e:
        settings = {}
        print('Cannot open settings.py and load the json content: {}'.format(e))    
    pythings_version = settings['pythings_version'] if 'pythings_version' in settings else 'FACTORY'
    
    if not pythings_version.upper() == 'FACTORY':
        path = fs_path+'/'+pythings_version
        print('Trying to load Pythings version {} from {}'.format(pythings_version,path))
        try:
            os.stat(path)
        except OSError:
            print('Proceeding with factory default version...')
            path=fs_path
        else:
            print('Updated version found, checking its consistency...')
            try:
                os.stat(path+'/version.py')
            except OSError:
                print('Error, proceeding with factory default version...')
                path=fs_path
            else:
                print('Valid updated version found.')
                sys.path.insert(0, path)
    else:
        path=fs_path

except Exception as e:
    print('Error, proceeding with factory defaults: ',type(e), str(e))
    path=fs_path

# Cleanup & un-load SAL if got loaded by hal
del settings
try: del sys.modules['sal']
except: pass
 
# Execute Pythings framework (from right path inserted above)
try:
    import init
    gc.collect()
    init.start()
except Exception as e:
    import handle_main_error
    handle_main_error.handle(e) 
    # TODO: Fallback on factory version?

    

