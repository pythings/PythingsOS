from common import http_get
import config
import globals
import logger

def check(my_version):
    try:
        if my_version:
            print('Checking for updates...')
            response = http_get('{}/static/dist/Pythings-MicroPython/last/version'.format(config.pythings_host))
            if response['status'] != b'200':
                raise Exception('Failed to get Pythings version, HTTP status code not 200 OK')
            if response['content'][0] != 'v':
                raise Exception('Failed to parse Pythings version (got {})'.format(response['content']))
            available_version = response['content'][1:]
            if float(available_version) > float(my_version):
                print('Update required (my version={}, available version={})'.format(my_version, available_version))
                import install
                install.BASE = '{}/static/dist/Pythings-MicroPython/last'.format(config.pythings_host)
                install('/last')
                print('\nUpdate OK, resetting...')
                import machine # Why we need to re-import? (necessary or NameError)
                machine.reset()
            else:
                print('No update required (my version={}, available version={})'.format(my_version, available_version))
        else:
            print('No my version set, skipping update check...')
    except Exception as e:
        print('Error in checking for updates: ',type(e), str(e), ', skipping...')   
        

def update_pythings(content):
    return False 
    # New pythings version to download?               
    try:
        if not globals.settings:
            logger.warning('Got empty settings! Backend problem?')
        else:
            if globals.settings['app_version'] != globals.running_app_version:
                logger.debug('Downloading the new app (running version = "{}"; required version = "{}")'.format(globals.running_app_version, globals.settings['app_version']))
                from utils import mv
                from http import download
                # Save backup for the app:
                mv('/app.py','/app_bk.py')
                # Ok, download
                download('{}/api/v1/apps/get/?aid={}&version={}&token={}'.format(globals.pythings_host, globals.aid, globals.settings['app_version'], globals.token), '/app.py')
                logger.info('Got new, updated app')
                return True
            else:
                logger.debug('No app update required. (running version = "{}"; required version = "{}")'.format(globals.running_app_version, globals.settings['app_version']))
                return False
    except Exception as e:
        import sys
        sys.print_exception(e)
        logger.error('Error in checking/updateing app ({}: {}), skipping...'.format(type(e), e))
        return False


