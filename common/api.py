
import cache
import logger
import json
from http import post
import gc

apiver='v0.2'

# Utility
def check_response(response):
    if response['status'] != b'200':
        try:
            msg=response['content']
            if not msg: msg=response 
        except Exception:
            msg=response
        raise Exception(msg)

# Apis
def apost(api, data={}):
    url = '{}/api/{}{}'.format(cache.backend,apiver,api)
    logger.debug('Calling API {} with data'.format(url),data)
    response = post(url, data=data)
    gc.collect()
    logger.info('Got response:',response)
    if response['content'] and response['content'] != '\n':
        response['content'] = json.loads(response['content']) 
    check_response(response)
    return response

def download(file_name, version, dest, what, system):
    logger.info('Downloading {} in'.format(file_name),dest) 
    response = post(cache.backend+'/api/'+apiver+'/'+what+'/get/', {'file_name':file_name, 'version':version, 'token':cache.token, 'system':system}, dest=dest)
    check_response(response)

# Report
def report(what, status, message=None):
    logger.info('Reporting "{}" as "{}" with message "{}"'.format(what,status,message[0:30]+'...' if message else None))
    response = apost('/things/report/', {'what':what,'status': status,'msg': message})
    logger.debug('Response:',response)
