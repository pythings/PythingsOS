import socket
import json
import logger
from hal import socket_readline,fspath

# Note: post and get will load a single line to avoid memory problems in case of error 500
# pages and so on (Pythings backend will always provide responses in one line).

def post(url, data):

    _, _, host, path = url.split('/', 3)
    port=80
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    try: s.settimeout(60)
    except: pass
    s.connect(addr) #Tryexcept this
    s.send(bytes('%s /%s HTTP/1.0\r\nHost: %s\r\n' % ('POST', path, host), 'utf8'))

    content = json.dumps(data)
    content_type = 'application/json'

    if content is not None:
        s.send(bytes('content-length: %s\r\n' % len(content), 'utf8'))
        s.send(bytes('content-type: %s\r\n' % content_type, 'utf8'))
        s.send(bytes('\r\n', 'utf8'))
        s.send(bytes(content, 'utf8'))
    else:
        s.send(bytes('\r\n', 'utf8'))

    # Status, msg etc.
    version, status, msg = socket_readline(s).split(None, 2)

    # Skip headers
    while socket_readline(s) and socket_readline(s) != b'\r\n': # added forst part to avid loops. TODO: merge.
        pass

    # Read data
    content = None
    while True:
        data = socket_readline(s)
        if data:      
            content = str(data, 'utf8')
            break   
        else:
            break
        
    s.close()
    return {'version':version, 'status':status, 'msg':msg, 'content':content}
           

def get(url):
    _, _, host, path = url.split('/', 3)
    port=80
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    try: s.settimeout(60)
    except: pass
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))

    # Status, msg etc.
    version, status, msg = socket_readline(s).split(None, 2)

    # Skip headers
    while socket_readline(s) != b'\r\n':
        pass

    # Read data
    while True:
        data = socket_readline(s)
        if data:
            content = str(data, 'utf8')
        else:
            break
    s.close() #TODO: add a finally for closing the connnection?
    return {'version':version, 'status':status, 'msg':msg, 'content':content}


def download(source,dest):
    logger.info('Downloading {} in {}'.format(source,dest)) 
    f = open(fspath+'/'+dest, 'w')
    _, _, host, path = (source).split('/', 3)
    port=80
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    try: s.settimeout(60)
    except: pass
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
 
    # Status, msg etc.
    version, status, msg = socket_readline(s).split(None, 2)

    if status != b'200':
        logger.error('Status {} trying to get '.format(status),source)
        f.close()
        s.close()
        return False

    # Skip headers
    while socket_readline(s) != b'\r\n': 
        pass 

    while True:
        data = s.recv(100)
        if data:
            f.write((str(data, 'utf8')))
        else:
            break
    f.close()
    s.close()
    return True
