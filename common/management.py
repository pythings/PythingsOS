import globals
import logger
from api import apost, report
import gc
from common import run_controlled

def system_management_task(chronos):
    
    updates=False
    
    # Call management API
    response = run_controlled(2,apost,api='/apps/management/')
    if response and 'content' in response: 
        content = response['content']
    else:
        logger.error('Error in receiving/parsing settings, skipping the rest of the management task!')
        return
    del response
    gc.collect()

    # Update settings, pythings, app. TODO: move to try/except?
    try:
        if 'settings' in content['data'] and content['data']['settings'] != globals.settings:   
            from updates_settings import update_settings
            if update_settings(content): updates='settings' 
        
        elif globals.settings['pythings_version'].upper() != 'FACTORY' and globals.settings['pythings_version'] != globals.running_pythings_version:
            logger.debug('Downloading the new pythings (running version = "{}"; required version = "{}")'.format(globals.running_pythings_version, globals.settings['pythings_version']))
            from updates_pythings import update_pythings
            if update_pythings(globals.settings['pythings_version']): updates='pythings' 
 
        else:
            if globals.settings['app_version'] != globals.running_app_version:
                logger.debug('Downloading the new app (running version = "{}"; required version = "{}")'.format(globals.running_app_version, globals.settings['app_version']))
                from updates_app import update_app
                if update_app(globals.settings['app_version']): updates='app'  

    except Exception as e:
        import sys
        sys.print_exception(e)
        logger.error('Error in checking/updating {} ({}: {}), skipping the rest...'.format(updates,type(e), e))
        return False

    gc.collect()

    # If updates, reboot.
    if updates:
        logger.info('Rebooting due to update')
        run_controlled(2,report,what='pythings', status='OK', message='Resetting due to {} update'.format(updates))
        import hal
        hal.reboot()

    # Data = remote command sent, here we use a sample
    app_data     = content['data']['app_data'] if 'app_data' in content['data'] else None
    app_data_id  = content['data']['app_data_id'] if 'app_data_id' in content['data'] else None
    app_data_rep = None

    # Call App's management
    if globals.app_management_task:
        try:
            print('67----------------------------',gc.mem_free())
            app_data_rep=globals.app_management_task.call(chronos, app_data)
            if app_data_id:
                run_controlled(2,report,what='management', status='OK', message={'app_data_id':app_data_id,'app_data_rep':app_data_rep})
            else:
                run_controlled(2,report,what='management', status='OK')
                
        except Exception as e:
            import sys
            sys.print_exception(e)
            logger.error('Error in executing app\'s management task: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='management', status='KO', message='{} {}'.format(e.__class__.__name__, e))
