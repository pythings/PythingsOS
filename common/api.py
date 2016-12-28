
import globals
import logger
import json
from http import post
import gc

version='v1'

def apost(api, data={}):
    url = '{}/api/{}{}'.format(globals.backend_addr,version,api)
    logger.debug('Calling API {} with data'.format(url),data)
    response = post(url, data=data)
    gc.collect()
    logger.debug('Got response:',response)
    if response['content'] and response['content'] != '\n':
        response['content'] = json.loads(response['content']) 
    logger.debug('Loaded json content and returning')

    if response['status'] != b'200':
        try:
            msg=response['content']['data']
        except Exception:
            msg=response
        raise Exception(msg)
    return response

def report(what, status, message=None):
    logger.info('Reporting "{}" as "{}" with message "{}"'.format(what,status,message))
    response = apost('/things/report/', {'what':what,'status': status,'message': message})
    logger.debug('Response:',response)
