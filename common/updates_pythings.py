
import globals
import logger
import os
from version import arch

BASE ='http://backend.pythings.io/static/dist/{}/'.format(arch)

def update_pythings(version):
    path='/'+version
    try:
        os.mkdir(path)
    except OSError as e:
        pass
    from http import download
    if not download(BASE+version+'/files.txt', path+'/files.txt'):
        return
    files_list = open(path+'/files.txt')
    for item in files_list.read().split('\n'):
        if 'file:' in item:
            filename=item.split(':')[2]
            if filename=='app.py': continue
            filesize=item.split(':')[1]
            download(BASE+version+'/'+filename, path+'/'+filename)
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
