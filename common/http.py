from pal import socket
import json
import logger
import hal
import pal
import env
import gc

def post(url, data, dest=None):
    use_ssl = env.settings['ssl'] if 'ssl' in env.settings else True
    try: token = env.token
    except AttributeError: token=None
    if  env.payload_encrypter and token:
        data = json.dumps(data)
        # Encrypt progressively
        encrypted=''
        while data:
            encrypted +=  env.payload_encrypter.encrypt_text(data[:12])
            data = data[12:]
        data =  {'encrypted': encrypted}

    if token: data['token'] = token
    port = 443 if (hal.HW_SUPPORTS_SSL and use_ssl) else 80
    host, path = url.split('/', 1)
    if ':' in host:
        port=int(host.split(':')[1])
        host=host.split(':')[0]
    logger.debug('Calling POST "{}:{}/{}" with data'.format(host,port,path),data)
    try:
        addr = socket.getaddrinfo(host, port)[0][-1]
    except IndexError:
        raise Exception('Cannot resolve host "{}"'.format(host))
    s = socket.socket()
    try: s.settimeout(60)
    except: pass

    # If socket connect fails do not have an exception when closing file in the finally
    if dest: f = None

    # Connect and handle SSL
    s.connect(addr)
    if hal.HW_SUPPORTS_SSL and use_ssl:
        s = pal.socket_ssl(s)
   
    try:
        
        if dest: f = open(dest, 'w')
        
        pal.socket_write(s, bytes('%s /%s HTTP/1.0\r\nHost: %s\r\n' % ('POST', path, host), 'utf8'))

        content = json.dumps(data)
        content_type = 'application/json'

        if content is not None:
            pal.socket_write(s, bytes('content-length: %s\r\n' % len(content), 'utf8'))
            pal.socket_write(s, bytes('content-type: %s\r\n' % content_type, 'utf8'))
            pal.socket_write(s, bytes('\r\n', 'utf8'))
            pal.socket_write(s, bytes(content, 'utf8'))
        else:
            pal.socket_write(s, bytes('\r\n', 'utf8'))

        # Status, msg etc.
        version, status, msg = pal.socket_readline(s).split(None, 2)
    
        # Skip headers
        while pal.socket_readline(s) != b'\r\n':
            pass
    
        # Read data
        content   = None
        stop      = False
        while True:
            data=''

            while len(data) < 39:
                last = str(pal.socket_read(s, 1), 'utf8')
                if len(last) == 0:
                    stop=True
                    break
                else:
                    # If newline and not dest, likely it is not a JSON but an error page. Break to avoid memory problems.
                    if not dest and last == '\n':
                        stop=True
                        break
                    data += last

            # Break now if len(data) == 0 which means that there is no more data in the socket at all.
            if len(data) == 0:
                break

            logger.debug('Received data', data)
            if dest and status == b'200':
                # load content, check if prev_content[-1] + content[1] == \n,
                if env.payload_encrypter:
                    content = env.payload_encrypter.decrypt_text(data)
                    #logger.debug('Decrypted data', content)
                else:
                    content = data
                f.write(content)
            else:
                if content is None:
                    content=''

                if env.payload_encrypter:
                    content += env.payload_encrypter.decrypt_text(data)
                    #logger.debug('Decrypted data', content)
                else:
                    content +=data

            # Cleanup & stop if it was the last data chunk
            del data
            gc.collect()
            if stop:
                break

        return {'version':version, 'status':status, 'msg':msg, 'content':content}
    except:
        raise
    finally:
        if dest and f:
            f.close()
        s.close()

