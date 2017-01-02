
import globals
import logger
import os
from system import system
from hal import get_fs_path
from api import apost, download

def update_pythings(version):
    
    files = apost(api='/pythings/get/', data={'version':version, 'list':True, 'system':system})['content']

    path = get_fs_path()+'/'+version
    try:
        os.mkdir(path)
    except OSError as e:
        pass

    for file_name in files:
        if file_name != 'version.py':
            download(file_name=file_name, version=version, system=system, dest='{}/{}'.format(path, file_name), what='pythings')
    for file_name in files:
        if file_name == 'version.py':
            download(file_name=file_name, version=version, system=system, dest='{}/{}'.format(path, file_name), what='pythings')
