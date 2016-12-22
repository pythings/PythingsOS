
import globals
import logger
import json
from http import post
import gc

version='v1'

def apost(api, data={}):
    try: token = globals.token
    except AttributeError: token=None
    if  globals.payload_encrypter and token:
        data =  {'encrypted': globals.payload_encrypter.encrypt_text(json.dumps(data))}
    if token: data['token'] = token
    url = '{}/api/{}{}'.format(globals.backend_addr,version,api)
    logger.debug('Calling API {} with data'.format(url),data)
    response = post(url, data=data)
    gc.collect()
    logger.debug('Got response:',response)
    if response['content'] and response['content'] != '\n':
        response['content'] = json.loads(response['content']) 
    if globals.payload_encrypter:
        decrypted_data = globals.payload_encrypter.decrypt_text(response['content']['data'])
        response['content']['data'] = json.loads(decrypted_data)
    logger.debug('Loaded json content and returning')

    if response['status'] != b'200':
        raise Exception(response['content']['data'])
    return response

def report(what, status, message=None):
    logger.info('Reporting "{}" as "{}" with message "{}"'.format(what,status,message))
    response = apost('/things/report/', {'what':what,'status': status,'message': message})
    logger.debug('Response:',response)
