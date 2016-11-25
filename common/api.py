
import globals
import logger
import json
from http import post
import gc

version='v1'

# Generic calls
def apost(api, data={}):
    try:
        data['token'] = globals.token
    except AttributeError:
        pass             
    url = '{}/api/{}{}'.format(globals.pythings_host,version,api)
    logger.debug('Calling API {} with data'.format(url),data) 
    response = post(url, data=data)
    gc.collect()
    logger.debug('Got response:',response)
    if response['content'] :
        response['content'] = json.loads(response['content']) 
    logger.debug('Loaded json content and returning')
    return response

def report(what, status, message=None):
    logger.info('Reporting "{}" as "{}" with message "{}"'.format(what,status,message))
    response = apost('/things/report/', {'what':what,'status': status,'message': message})
    logger.debug('Response:',response)
