
import cache
import logger

def update_settings(content):
    logger.debug('Storing received settings ({} <--> {})'.format(content['settings'], cache.settings))
    f = open(cache.root+'/settings.json', 'w')
    import json
    f.write(json.dumps(content['settings']))
    f.close()
    logger.info('Got new, updated settings')


