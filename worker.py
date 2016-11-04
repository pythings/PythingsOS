import globals
import logger
from api import apost, report
import gc
from common import run_controlled

def system_worker_task(chronos):
    
    # Call App's worker    
    if globals.app_worker_task:
        app_data = None
        try:
            print('97----------------------------',gc.mem_free())
            app_data = globals.app_worker_task.call(chronos)
            if app_data:
                run_controlled(2,apost,api='/msg/drop/', data={'msg': app_data })
            report('worker','OK')
        except Exception as e:
            import sys
            sys.print_exception(e)
            logger.error('Error in executing app\'s worker taks or sending its data: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='worker', status='KO', message='{} {}'.format(e.__class__.__name__, e))
            