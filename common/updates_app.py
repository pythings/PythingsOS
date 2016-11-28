import globals
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
        return False