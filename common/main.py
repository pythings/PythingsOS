import gc
import os
import sys

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
        else:
            print('Updated version found, checking its consistency...')
            try:
                os.stat(path+'/version')
            except OSError:
                print('Error, proceeding with factory default version...')
            else:
                print('Valid updated version found.')
                sys.path.append(path)
                os.chdir(path)
except Exception as e:
    import sys
    sys.print_exception(e)
    print('Error, proceeding with factory defaults: ',type(e), str(e))

del load_settings

        
# Execute Pythings framework
try:
    import startup
    gc.collect()
    startup.start()
    
except Exception as e:
    import handle_main_error
    handle_main_error.handle(e) # Fallback on factory defaults?
finally:
    os.chdir('/')
    

