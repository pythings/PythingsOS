import socket
import os

BASE ='http://backend.pythings.io/static/dist/ESP8266/v0.06'

def download(file,path,debug=False):
    print('\nDownloading', file, 'in', path)
    fullpath = path+file
    basepath = '/'.join(fullpath.split('/')[0:-1])
    try:
        os.stat(basepath)
    except OSError:
        print('Directory"', basepath,  '" does not exists, creating')
        os.mkdir(basepath)    
    if debug: print('Writing in {}'.format(fullpath))
    f = open(fullpath, 'w')
    remotepath=BASE+'/'+file
    print('Source:', remotepath)
    _, _, host, path = (remotepath).split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    line=None
    while line != b'\r\n':
        if debug: print(line)
        line = s.readline()
    while True:
        data = s.readline()
        if data: f.write((str(data, 'utf8')))
        else: break
    f.close()
    print('Download OK')

def doinstall(path='/'):   
    download('/files.txt', path)
    files_list = open(path+'/files.txt')
    for item in files_list.read().split('\n'):
        if 'file:' in item:
            filename=item.split(':')[2]
            filesize=item.split(':')[1]
            download(filename, path)
            if os.stat(filename)[6] != int(filesize):
                print('Aborting: file expected size={}, actual size={}.'.format(filesize,os.stat(filename)[6]))
                os.remove(filename)
                files_list.close()
                return
        else:
            if len(item)>0:
                print('Aborting: Got unexpected format in files list.')
                return
            
    files_list.close()

if __name__ == "__main__":
    doinstall()
