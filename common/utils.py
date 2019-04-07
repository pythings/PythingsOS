import os
from pal import get_re
import cache
import logger

def connect_wifi(wlan, essid, password):
    wlan.connect(essid, password)

def unquote(s):
    res = s.split('%')
    for i in range(1, len(res)):
        item = res[i]
        try:
            res[i] = chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            res[i] = '%' + item
    return "".join(res)

def load_param(param, default=None):
    try:
        with open(cache.root+'/{}'.format(param),'r') as f:
            param = f.readline().strip()
        return param
    except Exception as e:
        return default

def load_settings():
    import json
    settings = {}
    try:
        with open(cache.root+'/settings.json','r') as f:
            try:
                settings = json.loads(f.read())
            except Exception as e:
                logger.error('Cannot load json content: {}'.format(e))
    except Exception as e:
        logger.error('Cannot open settings.py: {}'.format(e))
    return settings

def mv(source,dest):
    try:
        try:
            os.remove(cache.root+'/'+dest)
        except:
            pass
        os.rename(cache.root+'/'+source, cache.root+'/'+dest)
    except:
        pass

def get_wifi_data():
    try:
        with open(cache.root+'/wifi','r') as f:
            essid = f.readline()[0:-1]
            password = f.readline()
    except:
        essid=None
        password=None
    return (essid,password)

def parseURL(url):
    parameters = {}
    path = get_re().search("(.*?)(\?|$)", url).group(1)
    if '?' in url:
        try:
            for keyvalue in url.split('?')[1].split('&'):
                parameters[unquote(keyvalue.split('=')[0])] = unquote(keyvalue.split('=')[1])
        except IndexError:
            pass
    return path, parameters
