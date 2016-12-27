import socket
import json
import logger
import hal

def post(url, data):
    port = 443 if hal.HW_SUPPORTS_SSL else 80 # TODO: port has to go after.
    url = 'https://'+url if hal.HW_SUPPORTS_SSL else 'http://'+url
    logger.info('Calling POST "{}" with data '.format(url),data)
    _, _, host, path = url.split('/', 3)
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    try: s.settimeout(60)
    except: pass

    if hal.HW_SUPPORTS_SSL:
        s = hal.socket_ssl(s)

    s.connect(addr)
    s.send(bytes('%s /%s HTTP/1.0\r\nHost: %s\r\n' % ('POST', path, host), 'utf8'))

    content = json.dumps(data)
    content_type = 'application/json'

    if content is not None:
        s.send(bytes('content-length: %s\r\n' % len(content), 'utf8'))
        s.send(bytes('content-type: %s\r\n' % content_type, 'utf8'))
        s.send(bytes('\r\n', 'utf8'))
        hal.socket_write(s, data=bytes(content, 'utf8'))
    else:
        s.send(bytes('\r\n', 'utf8'))

    # Status, msg etc.
    version, status, msg = hal.socket_readline(s).split(None, 2)

    # Skip headers
    while hal.socket_readline(s) != b'\r\n':
        pass

    # Read data
    content = None
    while True:
        data = hal.socket_readline(s)
        if data:      
            content = str(data, 'utf8')
            break   
        else:
            break

    s.close()
    return {'version':version, 'status':status, 'msg':msg, 'content':content}
           

def get(url):
    port = 443 if hal.HW_SUPPORTS_SSL else 80
    url = 'https://'+url if hal.HW_SUPPORTS_SSL else 'http://'+url
    logger.info('Calling GET "{}"'.format(url)) 
    _, _, host, path = url.split('/', 3)
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
    version, status, msg = hal.socket_readline(s).split(None, 2)

    # Skip headers
    while hal.socket_readline(s) != b'\r\n':
        pass

    # Read data
    while True:
        data = hal.socket_readline(s)
        if data:
            content = str(data, 'utf8')
        else:
            break
    s.close()
    # TODO: add a finally for closing the connection!
    return {'version':version, 'status':status, 'msg':msg, 'content':content}


def download(source,dest):
    port = 443 if hal.HW_SUPPORTS_SSL else 80
    source = 'https://'+source if hal.HW_SUPPORTS_SSL else 'http://'+source
    logger.info('Downloading {} in {}'.format(source,dest)) 
    f = open(dest, 'w')
    _, _, host, path = (source).split('/', 3)
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
    _, status, _ = hal.socket_readline(s).split(None, 2)

    if status != b'200':
        logger.error('Status {} trying to get '.format(status),source)
        f.close()
        s.close()
        return False

    # Skip headers
    while hal.socket_readline(s) != b'\r\n': 
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
