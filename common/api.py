
import globals
import logger
import json
from http import post
import gc

version='v0.2'

# Utility
def check_response(response):
    if response['status'] != b'200':
        try:
            msg=response['content']
        except Exception:
            msg=response
        raise Exception(msg)

# Apis
def apost(api, data={}):
    url = '{}/api/{}{}'.format(globals.backend,version,api)
    logger.debug('Calling API {} with data'.format(url),data)
    response = post(url, data=data)
    gc.collect()
    logger.debug('Got response:',response)
    if response['content'] and response['content'] != '\n':
        response['content'] = json.loads(response['content']) 
    logger.debug('Loaded json content and returning') 
    check_response(response)
    return response

def download(file_name, version, dest, what, arch):
    logger.info('Downloading {} in'.format(file_name),dest) 
    response = post(globals.backend+'/api/v1/'+what+'/get/', {'file_name':file_name, 'version':version, 'token':globals.token, 'arch':arch}, dest=dest)
    check_response(response)

# Report
def report(what, status, message=None):
    logger.info('Reporting "{}" as "{}" with message "{}"'.format(what,status,message))
    response = apost('/things/report/', {'what':what,'status': status,'msg': message})
    logger.debug('Response:',response)