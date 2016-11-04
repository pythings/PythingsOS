import socket
import json
import logger

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
    s.connect(addr) #Tryexcept this
    s.write('%s /%s HTTP/1.0\r\nHost: %s\r\n' % ('POST', path, host))

    content = json.dumps(data)
    content_type = 'application/json'

    if content is not None:
        s.write('content-length: %s\r\n' % len(content))
        s.write('content-type: %s\r\n' % content_type)
        s.write('\r\n')
        s.write(content)
    else:
        s.write('\r\n')

    # Status, msg etc.
    version, status, msg = s.readline().split(None, 2)

    # Skip headers
    while s.readline() != b'\r\n':
        pass

    # Read data
    content = None
    while True:
        data = s.readline()
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
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))

    # Status, msg etc.
    version, status, msg = s.readline().split(None, 2)

    # Skip headers
    while s.readline() != b'\r\n':
        pass

    # Read data
    while True:
        data = s.readline
        if data:
            content = str(data, 'utf8')
        else:
            break
    s.close() #TODO: add a finally for closing the connnection?
    return {'version':version, 'status':status, 'msg':msg, 'content':content}


def download(source,dest):
    logger.info('Downloading {} in {}'.format(source,dest)) 
    f = open(dest, 'w')
    _, _, host, path = (source).split('/', 3)
    port=80
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
 
    # Status, msg etc.
    version, status, msg = s.readline().split(None, 2)

    if status != b'200':
        logger.error('Status {} trying to get '.format(status),source)
        f.close()
        s.close()
        return False

    # Skip headers
    while s.readline() != b'\r\n': 
        pass 

    while True:
        data = s.readline() #data = s.recv(100)?
        if data:
            f.write((str(data, 'utf8')))
        else:
            break
    f.close()
    s.close()
    return True
