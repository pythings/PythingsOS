
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
        raise Exception('Update aborted: error in downloading files list.')
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
                raise Exception('Update aborted: file expected size={}, actual size={}.'.format(filesize,os.stat(path+'/'+filename)[6]))
        else:
            if len(item)>0:
                files_list.close()
                raise Exception('Update aborted: got unexpected format in files list.')
    files_list.close()

