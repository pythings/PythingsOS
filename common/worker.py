import globals
import logger
from api import apost, report
import gc
import sal
from common import run_controlled

def system_worker_task(chronos):
    
    # Call App's worker    
    if globals.app_worker_task:
        worker_msg = None
        try:
            logger.debug('Mem free:', sal.get_mem_free())
            worker_msg = globals.app_worker_task.call(chronos)
            if worker_msg:
                run_controlled(2,apost,api='/apps/worker/', data={'msg': worker_msg })
            report('worker','OK')
        except Exception as e:
            print(sal.get_traceback(e))
            logger.error('Error in executing app\'s worker taks or sending its data: {} {}'.format(e.__class__.__name__, e))
            run_controlled(2,report,what='worker', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, sal.get_traceback(e)))
            