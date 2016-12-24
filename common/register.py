import hal
import logger
import globals
from common import run_controlled
from api import apost

def preregister():
    from crypto_rsa import Srsa
    pubkey = 28413003199647341169755148817272580434684756919496624803561225904937920874272008267922241718272669080997784342773848675977238304083346116914731539644572572184061626687258523348629880944116435872100013777281682624539900472318355160325153486782544158202452609602511838141993451856549399731403548343252478723563
    logger.info('Pre-registering myself with aes128cbc key="{}"'.format(globals.payload_encrypter.key))
    response = run_controlled(None,
                              apost,
                              api='/things/preregister/',
                              data={'key': Srsa(pubkey).encrypt_text(str(globals.payload_encrypter.key)),
                                    'type': 'aes128ecb',
                                    'enc': 'srsa1'})        
    if not response:
        raise Exception('Empty Response from preregister')
    
    return response['content']['data']['token']



def register():
    logger.info('Registering myself with tid={} and aid={}'.format(globals.tid,globals.aid))
    response = run_controlled(None,
                                     apost,
                                     api='/things/register/',
                                     data={'tid':globals.tid,
                                           'aid': globals.aid,
                                           'running_app_version': globals.running_app_version,
                                           'running_os_version': globals.running_os_version,
                                           'pool': globals.pool,
                                           'settings': globals.settings,
                                           'frozen_os':globals.frozen_os})
    if not response:
        raise Exception('Empty Response from register')
    
    return (response['content']['data']['token'], response['content']['data']['epoch_s'])
