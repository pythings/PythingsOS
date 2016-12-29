
import globals
import logger
import os
from arch import arch
from hal import fspath
from api import apost, download
from arch import arch

def update_pythings(version):
    
    files = apost(api='/pythings/get/', data={'version':version, 'list':True, 'arch':arch})['content']['data']

    path = fspath+'/'+version
    try:
        os.mkdir(path)
    except OSError as e:
        pass

    for file_name in files:
        if file_name != 'version.py':
            print('FILE::', file_name, files[file_name])
            download(file_name=file_name, version=version, arch=arch, dest='{}/{}'.format(fspath, file_name), what='pythings')
    for file_name in files:
        if file_name == 'version.py':
            print('FILE::', file_name, files[file_name])
            download(file_name=file_name, version=version, arch=arch, dest='{}/{}'.format(fspath, file_name), what='pythings')
