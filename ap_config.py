#---------------------
#  Imports
#---------------------

import machine
import network
import ure
import socket
import time
from common import connect_wifi
from webserver import Sender, header, footer, parseURL


#---------------------
#  Main functions
#---------------------

def ap_config(timeout_s=60, lock_session=False):
    print('Starting AP web config')
    # Set up startup
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(0)
    s.settimeout(timeout_s)
    print('Listening on', addr)
    CONF_PAGE_ACCESSED = False
    
    while True:
        try:
            print('Waiting for a connection..')
            
            # Handle client connection
            cl, addr = s.accept()
            
            print('client connected from', addr)
            if lock_session:
                s.settimeout(None)
            CONF_PAGE_ACCESSED = True

            # Handle request
            request = str(cl.recv(1024))

            # Parse GET request
            get_request_data = ure.search("GET (.*?) HTTP\/1\.1", request)
            if get_request_data:
                #print("obj: ", obj.group(1))
                path, parameters = parseURL(get_request_data.group(1))
                print('Path: %s, Params: %s <br />'  % (path, parameters))
                if 'favicon' in path:
                    print('Requested favicon, closing connection.')
                    cl.close()
                
                            
            # Init sender
            sender = Sender(cl=cl)
     
            # Send HTML page header       
            sender.send(text=header())
            
            # Init WLAN in STA mode
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True) # Do not miss this :)
 
            # Do we have to configure Wifi?
            if 'essid' in parameters and 'password' in parameters:
                connect_wifi(wlan, parameters['essid'], parameters['password'])
                count=0
                while not wlan.isconnected():
                    count+=1
                    sender.send(text=' ')
                    print('WLAN connected:', str(wlan.isconnected()))
                    time.sleep(1)
                    if count > 10:
                        print ('timed out.')
                        break
                if count <10:
                    print ('Connected!')

                # Check it works..
                # get something form Pythings..
  
            # Do we have to just exit ?
            if 'close' in parameters:
                break
                
            # Scan for wifi networks
            nets = wlan.scan() 
                
            # Handle scan results
            sender.send(text='<center>Wifi connected: %s <br/><br/>' % (str(wlan.isconnected()))) 
            text = '<form action="./setWiFi" method="get">Network: <select name="essid">'
            for net in nets:
                net_name = str(net[0])[2:-1]
                text += '<option value="%s">%s (%s)</option>' % (net_name, net_name, str(net[3]+100))
            text +='</select><br/>'
            text += '''Password: <input type="text" name="password"><br/><br/><input type="submit" value="Connect"></form>
<form action="./setWiFi" method="get"><input type="hidden" name="close" value=True"><input type="submit" value="Close"></form></center>'''
            sender.send(text=text)
            
            # Send HTML footer
            sender.send(text=footer(), last=True)
            
            # Close client connection
            print('Ok, closing client connection.')
            cl.close()
        
        except OSError as e:
            if str(e) == "[Errno 110] ETIMEDOUT":
                if CONF_PAGE_ACCESSED:
                    #continue
                    print ('Exiting due to no activity')
                    s.close()
                    break
                
                else:
                    print ('Exiting due to no incoming connections')
                    s.close()
                    break
            print(e)

    return

if __name__ == "__main__":
    ap_config(60)


