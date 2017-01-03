import logger
import globals
from common import run_controlled
from api import apost

def register():
    logger.info('Registering myself with tid={} and aid={}'.format(globals.tid,globals.aid))
    response = run_controlled(None,
                                     apost,
                                     api='/things/register/',
                                     data={'tid': globals.tid,
                                           'aid': globals.aid,
                                           'app_version': globals.app_version,
                                           'pythings_version': globals.pythings_version,
                                           'pool': globals.pool,
                                           'frozen':globals.frozen})
    if not response:
        raise Exception('Empty Response from register')
    
    return (response['content']['token'], response['content']['epoch'])
