
import env
import logger

def update_settings(content):
    logger.debug('Storing received settings ({} <--> {})'.format(content['settings'], env.settings))
    f = open(env.root+'/settings.json', 'w')
    import json
    f.write(json.dumps(content['settings']))
    f.close()
    logger.info('Got new, updated settings')


