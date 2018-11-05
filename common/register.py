import logger
import cache
from common import run_controlled
from api import apost

def register():
    logger.info('Registering myself with tid={} and aid={}'.format(cache.tid,cache.aid))
    response = run_controlled(None,
                                     apost,
                                     api='/things/register/',
                                     data={'tid': cache.tid,
                                           'aid': cache.aid,
                                           'app_version': cache.app_version,
                                           'pythings_version': cache.pythings_version,
                                           'pool': cache.pool,
                                           'frozen':cache.frozen})
    if not response:
        raise Exception('Empty Response from register')
    
    return (response['content']['token'], response['content']['epoch'])
