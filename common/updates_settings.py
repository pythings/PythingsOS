
import globals
import logger
from hal import get_fs_path

def update_settings(content):
    logger.debug('Storing received settings ({} <--> {})'.format(content['settings'], globals.settings))
    f = open(get_fs_path()+'/settings.json', 'w')
    import json
    f.write(json.dumps(content['settings']))
    f.close()
    logger.info('Got new, updated settings')


