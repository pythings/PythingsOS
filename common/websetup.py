
import network
import socket
import time
import logger
import json
import ure
from utils import *
import hal
from platform import platform
from version import version
import gc

def websetup(timeout_s=60, lock_session=False):
    logger.info('Starting WebSetup')
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(0)
    s.settimeout(timeout_s)
    #logger.info('Listening on ', addr)
    
    # Start AP mode and disable client mode
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="Thing_{}".format(hal.get_tid()), authmode=network.AUTH_WPA_WPA2_PSK, password="NewThing")

    logger.info('Done, waiting for a connection... ({}s)'.format(timeout_s))

    while True:
        try:
            gc.collect()
            
            # Handle client connection
            cl, addr = s.accept()
            logger.info('Incoming client connection from', addr[0])
            s.settimeout(None)

            # Read request
            request = str(cl.recv(1024))

            # Parse GET request
            get_request_data = ure.search("GET (.*?) HTTP\/1\.1", request)
            if get_request_data:
                path, parameters = parseURL(get_request_data.group(1))
                #logger.debug('Got request for path = "{}" with params = "{}"'.format(path, parameters))
            else:
                path = []
                parameters = []

            cl.write('HTTP/1.0 200 OK\r\n')
            cl.write('Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n');
            cl.write("Access-Control-Allow-Origin: *\r\n");
            cl.write("Access-Control-Allow-Credentials: true\r\n");
            cl.write("Access-Control-Allow-Headers: X-CSRFToken, ACCEPT, CONTENT-TYPE, X-CSRF-TOKEN, Content-Type, Authorization, X-Requested-With\r\n");

            if not get_request_data: # an OPTIONS, basically
                #logger.debug('no GET data in request')
                cl.write('Content-Length: 0\r\n\r\n')
                cl.close()
                continue
            def set_api():
                cl.write('Content-Type: application/json\r\n')
                cl.write('\r\n')
            def set_page():
                cl.write('Content-Type: text/html\r\n')
                cl.write('\r\n')

            # Close connection if requesting favicon
            if 'favicon' in path:
                #logger.debug('Requested favicon, closing connection')
                set_api()
                cl.close()
            
            # This is an API call
            elif 'cmd' in parameters:
                logger.info('Called API with cmd={}'.format(parameters['cmd']))
                set_api()
                cmd = parameters['cmd']
                essid = None
                if 'essid' in parameters: essid = parameters['essid']   
                password = None
                if 'password' in parameters: password = parameters['password']                    

                # Set app command
                if cmd=='set_app':
                    #logger.debug('Called set app API')
                    aid = None
                    aid = parameters['aid']
                    if aid is None:
                        cl.write(json.dumps({'status':'ERROR'}))
                    else:
                        with open('/aid','w') as f:
                            f.write(aid)
                    cl.write(json.dumps({'status':'OK', 'aid': load_param('aid',None)}))

                # Set apn command
                if cmd=='set_apn':
                    #logger.debug('Called set app API')
                    apn = None
                    apn = parameters['apn']
                    if apn is None:
                        cl.write(json.dumps({'status':'ERROR'}))
                    else:
                        with open('/apn','w') as f:
                            f.write(apn)
                    cl.write(json.dumps({'status':'OK', 'apn': load_param('apn',None)}))

                # Check command
                if cmd=='check':
                    import os
                    #logger.debug('Called check API')
                    cl.write(json.dumps({'status':'OK', 'platform': platform, 'version': version, 'aid':load_param('aid',None)}))
                
                # Check_wifi command
                if cmd=='check_wifi':
                    #logger.debug('Called check_wifi API')
                    sta.active(True)
                    essid='Unknown'
                    isconnected=False
                    essid,password = get_wifi_data()
                    if essid:
                        connect_wifi(sta, essid, password)
                        time.sleep(25)
                    isconnected = sta.isconnected()
                    sta.active(False) 
                    cl.write(json.dumps({'status':'OK', 'isconnected':isconnected, 'essid':essid}))
                
                # Scan command
                elif cmd == 'scan':
                    #logger.debug('Called scan API')
                    sta.active(True)
                    nets = sta.scan() 
                    sta.active(False)
                    cl.write(json.dumps(nets))
                          
                # Join command                  
                elif cmd == 'join':
                    #logger.debug('Called join API')
                    if password is None or essid is None:
                        cl.write(json.dumps({'status': 'ERROR'}))
                    else:
                        sta.active(True)
                        connect_wifi(sta, essid, password)
                        time.sleep(25)
                        isconnected = sta.isconnected()
                        saved = False
                        if isconnected:
                            try:
                                with open('/wifi','w') as f:
                                    f.write('{}\n{}'.format(essid,password))
                                saved=True
                            except:
                                saved=False
                        sta.active(False)
                        cl.write(json.dumps({'status':'OK', 'isconnected':isconnected, 'essid':essid, 'saved':saved}))
                
                # Close command
                elif cmd == 'close':
                    #logger.debug('Called close API')
                    cl.write(json.dumps({'status': 'OK'}))
                    cl.close()
                    s.close()
                    break

            else:
                #logger.debug('Serving main page')
                set_page()
                cl.write('Please go to your vendor\'s Website to configure this device.\r\n')

            # Close client connection at the end
            #logger.info('Closing client connection')
            cl.close()
        
        except OSError as e:
            if str(e) == "[Errno 110] ETIMEDOUT":
                #logger.info('Exiting due to no incoming connections')
                s.close()
                break
            import sys
            sys.print_exception(e)
            #logger.error(str(e))
            try: cl.close()
            except: pass
            try: s.close()
            except: pass
            time.sleep(3)
