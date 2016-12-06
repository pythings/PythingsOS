import globals
import logger
from api import apost, report
import gc
import hal
from common import run_controlled


def system_worker_task(chronos):
    
    # Call App's worker    
    if globals.app_worker_task:
        app_data = None
        try:
            logger.debug('Mem free:', hal.mem_free())
            app_data = globals.app_worker_task.call(chronos)
            if app_data:
                run_controlled(2,apost,api='/msg/drop/', data={'msg': app_data })
            report('worker','OK')
        except Exception as e:
            print(hal.get_traceback(e))
            logger.error('Error in executing app\'s worker taks or sending its data: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='worker', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, hal.get_traceback(e)))
            