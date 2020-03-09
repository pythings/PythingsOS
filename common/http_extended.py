from pal import socket
import json
import logger
import hal
import pal
import env
import gc
import network
from utils import load_param
from SIM800L import Modem
from platform import platform

class Uart(object):

    def __init__(self, softuart):
        self.softuart=softuart
    
    def write(self, string):
        self.softuart.flush()
        self.softuart.write(string)

    def readline(self):
        line=bytes()
        while True:
            char = chr(self.softuart.get())            
            if char == '\x00':
                return line
            line += char.encode('utf8')
            if char == '\n':
                return line

# Do we have a modem configured?
try:
    env.apn
except AttributeError:
    env.apn = load_param('apn', None)

# Should we use AT-based, modem POST?
if (not network.WLAN(network.STA_IF).isconnected()) and env.apn:
    logger.debug('Using AT post')
    use_at_post = True
else:
    logger.debug('Using socket post')
    use_at_post = False

# Define AT-based post for AT modems
def at_post(url, data, dest=None):
    
    # Do we have the Modem ready?
    try:
        env.modem
    except AttributeError:
        # Do we have to load custom pins?
        modem_pins = load_param('modem_pins', None)
        if modem_pins:
            MODEM_PWKEY_PIN, MODEM_RST_PIN, MODEM_POWER_ON_PIN, MODEM_TX_PIN, MODEM_RX_PIN = [int(pin) if pin != 'None' else None for pin in modem_pins.split(',')]

        # Create new modem object on the right Pins
        if platform.startswith('esp8266'):
        
            from machine import SOFTUART
            uart=Uart(SOFTUART(tx = MODEM_TX_PIN if modem_pins else hal.MODEM_TX_PIN,
                               rx = MODEM_RX_PIN if modem_pins else hal.MODEM_RX_PIN,
                               baudrate=9600))
            env.modem = Modem(uart)

        else:        
            env.modem = Modem(MODEM_PWKEY_PIN    = MODEM_PWKEY_PIN if modem_pins else hal.MODEM_PWKEY_PIN,
                              MODEM_RST_PIN      = MODEM_RST_PIN if modem_pins else hal.MODEM_RST_PIN,
                              MODEM_POWER_ON_PIN = MODEM_POWER_ON_PIN if modem_pins else hal.MODEM_POWER_ON_PIN,
                              MODEM_TX_PIN       = MODEM_TX_PIN if modem_pins else hal.MODEM_TX_PIN,
                              MODEM_RX_PIN       = MODEM_RX_PIN if modem_pins else hal.MODEM_RX_PIN)
        env.modem.initialize()
    
    # Always connect, as if it is already connected won't do anything
    env.modem.connect(apn=env.apn)

    #----------------------
    #  Post start
    #----------------------

    try: token = env.token
    except AttributeError: token=None    
    if token: data['token'] = token  
    logger.debug('Calling POST "{}" with data'.format(url),data)

    # If POST fails do not have an exception when closing file in the finally
    if dest: f = None

    try:
        if dest: f = open(dest, 'w')    
        
        # Execute POST
        response = env.modem.http_request('http://'+url, 'POST', json.dumps(data), 'application/json')
        logger.debug('Received status code', response.status_code )
        logger.debug('Received content', response.content)
        status  = response.status_code   
        content = response.content

        if dest and status == 200:
            f.write(content)

        else:
            if content is None:
                content = ''

        return {'version':None, 'status':status, 'msg':None, 'content':content}
    except:
        raise
    finally:
        if dest and f:
            f.close()

# Define socket-based post
from http import post as socket_post

# Define wrapper post
def post(url, data, dest=None):
    if use_at_post:
        return at_post(url, data, dest=dest)
    else:
        return socket_post(url, data, dest=dest)


