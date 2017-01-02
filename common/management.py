import globals
import logger
from api import apost, report
import gc
from common import run_controlled
import hal
import sal

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

    # Update settings, Pythings and App.
    try:
        if 'settings' in content and content['settings'] != globals.settings:
            updates='Settings'
            from updates_settings import update_settings
            update_settings(content)

        elif not globals.frozen and globals.settings['pythings_version'].upper() != 'FACTORY' and globals.settings['pythings_version'] != globals.pythings_version:
            updates='Pythings' 
            logger.debug('Downloading new Pythings (running version = "{}"; required version = "{}")'.format(globals.pythings_version, globals.settings['pythings_version']))
            from updates_pythings import update_pythings
            update_pythings(globals.settings['pythings_version'])

        else:
            if globals.settings['app_version'] != globals.app_version:
                updates='App' 
                logger.debug('Downloading new App (running version = "{}"; required version = "{}")'.format(globals.app_version, globals.settings['app_version']))
                from updates_app import update_app
                update_app(globals.settings['app_version'])

    except Exception as e:
        print(sal.get_traceback(e))
        logger.error('Error in management task while updating {} ({}: {}), skipping the rest...'.format(updates, e.__class__.__name__, e))
        run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, sal.get_traceback(e)))
        return False

    gc.collect()

    # If updates, reboot.
    if updates:
        logger.info('Rebooting due to update')
        run_controlled(2,report,what='pythings', status='OK', message='Resetting due to {} update'.format(updates))
        hal.reboot()

    # Management Command (cmd), Command ID (cid) and Management Reply
    msg = content['msg'] if 'msg' in content else None
    mid = content['mid'] if 'mid' in content else None
    rep = None

    # Call App's management
    if globals.app_management_task:
        try:
            logger.debug('Mem free:', sal.get_mem_free())
            rep=globals.app_management_task.call(chronos, msg)
            if mid:
                run_controlled(2,report,what='management', status='OK', message={'mid':mid,'rep':rep})
            else:
                run_controlled(2,report,what='management', status='OK')
                
        except Exception as e:
            import sys
            sal.get_traceback(e)
            logger.error('Error in executing app\'s management task: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='management', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, sal.get_traceback(e)))
