import env
import logger
from api import apost, report
import gc
import pal
from common import run_controlled

def system_worker_task(chronos):
    
    # Call App's worker    
    if env.app_workerTask:
        worker_msg = None
        try:
            logger.debug('Mem free:', pal.get_mem_free())
            worker_msg = env.app_workerTask.call()
            if worker_msg:
                run_controlled(2,apost,api='/apps/worker/', data={'msg': worker_msg })
            report('worker','OK')
        except Exception as e:
            logger.error('Error in executing app\'s worker taks or sending its data: {} {}'.format(e.__class__.__name__, e))
            logger.debug(pal.get_traceback(e))
            run_controlled(2,report,what='worker', status='KO', message='{} {} ({})'.format(e.__class__.__name__, e, pal.get_traceback(e)))
            