
import cache
import logger
import os
from platform import platform
from api import apost, download

def update_pythings(version):
    
    files = apost(api='/pythings/get/', data={'version':version, 'list':True, 'platform':platform})['content']

    path = cache.root+'/'+version
    try:
        os.mkdir(path)
    except OSError as e:
        pass

    for file_name in files:
        if file_name != 'version.py':
            download(file_name=file_name, version=version, platform=platform, dest='{}/{}'.format(path, file_name), what='pythings')
    for file_name in files:
        if file_name == 'version.py':
            download(file_name=file_name, version=version, platform=platform, dest='{}/{}'.format(path, file_name), what='pythings')
