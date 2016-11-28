
import globals
import logger
import os
from arch import arch

def update_pythings(version):
    source='http://backend.pythings.io/static/dist/PythingsOS/{}/{}'.format(version,arch)
    path='/'+version
    try:
        os.mkdir(path)
    except OSError as e:
        pass
    from http import download
    if not download(source+'/files.txt', path+'/files.txt'):
        return False
    files_list = open(path+'/files.txt')
    for item in files_list.read().split('\n'):
        if 'file:' in item:
            filename=item.split(':')[2]
            if filename=='app.py': continue
            filesize=item.split(':')[1]
            download(source+'/'+filename, path+'/'+filename)
            if os.stat(path+'/'+filename)[6] != int(filesize):
                logger.error('Aborting: file expected size={}, actual size={}.'.format(filesize,os.stat(path+'/'+filename)[6]))
                os.remove(path+'/'+filename)
                files_list.close()
                return False
        else:
            if len(item)>0:
                logger.error('Aborting: Got unexpected format in files list.')
                files_list.close()
                return False
    files_list.close()
    return True
