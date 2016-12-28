import globals
import logger
from utils import mv
from api import apost,download
from hal import fspath
from arch import arch

def update_app(version):
    files = apost(api='/apps/get/', data={'version':version, 'list':True})['content']['data']
    # First of all remove /app.py to say that there is no valid App yet (download is in progress)
    import os
    try: os.remove(fspath+'/app.py')
    except: pass
    for file_name in files:
        if file_name in ['worker_task.py','management_task.py']:
            download(file_name=file_name, version=version, dest='{}/{}'.format(fspath, file_name),what='apps',arch=arch) 
        else:
            logger.info('NOT downloading "{}" as in forbidden list'.format(file_name))
    with open(fspath+'/app.py','w') as f:
        f.write('\nversion=\'{}\''.format(version))
    logger.info('Got new, updated app')
