import globals
import logger
from api import apost, report
import gc
from common import run_controlled
import hal

def system_management_task(chronos):
    
    updates=False
    
    # Call management API
    response = run_controlled(2,apost,api='/apps/management/')
    if response and 'content' in response: 
        content = response['content']
    else:
        logger.error('Error in receiving/parsing stg, skipping the rest of the management task!')
        return
    del response
    gc.collect()

    # Update stg, OS and App.
    try:
        if 'stg' in content and content['stg'] != globals.stg:
            updates='Settings'
            from updates_settings import update_settings
            update_settings(content)

        elif not globals.fzp and globals.stg['pythings_version'].upper() != 'FACTORY' and globals.stg['pythings_version'] != globals.rpv:
            updates='Pythings' 
            logger.debug('Downloading the new pythings (running version = "{}"; required version = "{}")'.format(globals.rpv, globals.stg['pythings_version']))
            from updates_pythings import update_pythings
            update_pythings(globals.stg['pythings_version'])

        else:
            if globals.stg['sav'] != globals.rav:
                updates='App' 
                logger.debug('Downloading the new app (running version = "{}"; required version = "{}")'.format(globals.rav, globals.stg['sav']))
                from updates_app import update_app
                update_app(globals.stg['sav'])

    except Exception as e:
        print(hal.get_traceback(e))
        logger.error('Error in management task while updating {} ({}: {}), skipping the rest...'.format(updates, e.__class__.__name__, e))
        run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))
        return False

    gc.collect()

    # If updates, reboot.
    if updates:
        logger.info('Rebooting due to update')
        run_controlled(2,report,what='pythings', status='OK', message='Resetting due to {} update'.format(updates))
        hal.reboot()

    # Data = remote command sent, here we use a sample
    app_data     = content['apd'] if 'apd' in content else None
    app_data_id  = content['did'] if 'did' in content else None
    app_data_rep = None

    # Call App's management
    if globals.app_management_task:
        try:
            logger.debug('Mem free:', hal.mem_free())
            app_data_rep=globals.app_management_task.call(chronos, app_data)
            if app_data_id:
                run_controlled(2,report,what='management', status='OK', message={'did':app_data_id,'rep':app_data_rep})
            else:
                run_controlled(2,report,what='management', status='OK')
                
        except Exception as e:
            import sys
            hal.get_traceback(e)
            logger.error('Error in executing app\'s management task: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))
