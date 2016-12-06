
import globals
import logger

def update_settings(content):
    logger.debug('Storing received settings ({} <--> {})'.format(content['data']['settings'], globals.settings))
    # TODO: Try load contents to validate?
    # Save backup for the settings file:
    from utils import mv
    mv('/settings.json','/settings_bk.json')
    # Ok, dump new settings
    f = open('/settings.json', 'w')
    import json
    f.write(json.dumps(content['data']['settings']))
    f.close()
    globals.settings = content['data']['settings']
    logger.info('Got new, updated settings')


