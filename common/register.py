import logger
import env
from common import run_controlled
from api import apost
from platform import platform

def register():
    logger.info('Registering myself with tid={} and aid={}'.format(env.tid,env.aid))
    response = run_controlled(None,
                                     apost,
                                     api='/things/register/',
                                     data={'tid': env.tid,
                                           'aid': env.aid,
                                           'app_version': env.app_version,
                                           'pythings_version': env.pythings_version,
                                           'pool': env.pool,
                                           'frozen':env.frozen,
                                           'platform':platform})
    if not response:
        raise Exception('Empty Response from register')
    
    return (response['content']['token'], response['content']['epoch'])
