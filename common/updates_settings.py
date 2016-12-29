
import globals
import logger
from hal import fspath

def update_settings(content):
    logger.debug('Storing received settings ({} <--> {})'.format(content['stg'], globals.stg))
    f = open(fspath+'/stg.json', 'w')
    import json
    f.write(json.dumps(content['stg']))
    f.close()
    logger.info('Got new, updated settings')


