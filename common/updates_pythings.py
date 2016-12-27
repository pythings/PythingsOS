
import globals
import logger
import os
from arch import arch
from hal import fspath

def update_pythings(version):
    source='backend.pythings.io/static/dist/PythingsOS/{}/{}'.format(version,arch)
    path=fspath+'/'+version
    try:
        os.mkdir(path)
    except OSError as e:
        pass
    from http import download
    if not download(source+'/files.txt', path+'/files.txt'):
        raise Exception('PythingsOS download failed')
    files_list = open(path+'/files.txt')
    for item in files_list.read().split('\n'):
        if 'file:' in item:
            filename=item.split(':')[2]
            if filename=='app.py': continue
            filesize=item.split(':')[1]
            download(source+'/'+filename, path+'/'+filename)
            if os.stat(path+'/'+filename)[6] != int(filesize):
                os.remove(path+'/'+filename)
                files_list.close()
                raise Exception('File expected size={}, actual size={}.'.format(filesize,os.stat(path+'/'+filename)[6]))
        else:
            if len(item)>0:
                raise Exception('Got unexpected format in files list.')
                files_list.close()
    files_list.close()
