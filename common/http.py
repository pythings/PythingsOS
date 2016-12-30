import socket
import json
import logger
import hal
import globals

def post(url, data, dest=None):
    print('POST: url',url)
    try: token = globals.token
    except AttributeError: token=None
    if  globals.payload_encrypter and token:
        data = json.dumps(data)
        # Encrypt progressively
        encrypted=''
        while data:
            encrypted +=  globals.payload_encrypter.encrypt_text(data[:12])
            data = data[12:]
        data =  {'encrypted': encrypted}

    if token: data['token'] = token
    port = 443 if hal.HW_SUPPORTS_SSL else 80
    host, path = url.split('/', 1)
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    logger.info('Calling POST "{}:{}/{}" with data'.format(host,port,path),data)
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    try: s.settimeout(60)
    except: pass

    use_ssl = globals.settings['ssl'] if 'ssl' in globals.settings else True
    if hal.HW_SUPPORTS_SSL and use_ssl:
        s = hal.socket_ssl(s)

    if dest: f = None # If socket connect fails do not have an exception when closing file
    s.connect(addr)
    if dest: f = open(dest, 'w')
    try:
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
        content   = None
        prev_last = None
        stop      = False
        while True:
            data=''
            if globals.payload_encrypter:
                if content is None:
                    str(s.recv(1), 'utf8')

                while len(data) < 39:
                    last = str(s.recv(1), 'utf8')
                    if len(last) == 0:
                        stop=True
                        break
                    data += last
                if stop:
                    break
                if data=='"':
                    continue
                logger.info('Received encrypted data', data.replace('\n',''))
                if dest and status == b'200' and data !='"':
                    # load content, check if prev_content[-1] + content[1] == \n,
                    content = globals.payload_encrypter.decrypt_text(data).replace('\\n','\n')
                    #logger.info('Decrypted data', data)
                    if prev_last is not None:
                        if prev_last =='\\' and content[0] == 'n':
                            f.write('\n'+ content[1:-1])
                            #logger.info('Writing data', content[1:-1])
                        else:
                            f.write(prev_last+content[:-1])
                            #logger.info('Writing data', prev_last+content[:-1])

                    else:
                        # We start from position 1 to avoid the extra "' char added by the backend
                        f.write(content[1:-1])
                    prev_last = content[-1]
                    # ..and we will never write the last prev_last as it is the '"' char added by the backend
                else:
                    if content is None: content=''
                    try:
                        content += globals.payload_encrypter.decrypt_text(data)
                    except Exception as e:
                        logger.error('Cannot decrypt text ({})'.format(e.__class__.__name__))
            else:
                data = hal.socket_readline(s)
                if data:
                    if dest:
                        f.write(str(data, 'utf8').replace('\\n','\n'))
                    else: 
                        content = str(data, 'utf8')
                        break   
                else:
                    break
        return {'version':version, 'status':status, 'msg':msg, 'content':content}
    except:
        raise
    finally:
        if dest and f:
            f.close()
        s.close()

