import os
import ure

def connect_wifi(wlan, essid, password):
    print("Connecting with: ", essid)
    print("Using password: ", password)
    wlan.connect(essid, password)

def unquote(s):
    res = s.split('%')
    for i in range(1, len(res)): # no xrange as not available for this micro.
        item = res[i]
        try:
            res[i] = chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            res[i] = '%' + item
    return "".join(res)

def load_param(param, default=None):
    try:
        with open('/{}'.format(param),'r') as f:
            param = f.readline()
        return param
    except Exception as e:
        return default

def load_settings():
    import json
    settings = {}
    try:
        with open('/settings.json','r') as f:
            settings = json.loads(f.read())
    except Exception as e:
        print('Cannot open settings.py and load the json content: {}'.format(e))
    return settings

def mv(source,dest):
    try:
        import os
        try:
            os.remove(dest)
        except:
            pass
        os.rename(source, dest)
    except:
        pass



def get_wifi_data():
    try:
        with open('/wifi','r') as f:
            essid = f.readline()[0:-1]
            password = f.readline()
    except:
        essid=None
        password=None
    return (essid,password)

def parseURL(url):
    parameters = {}
    path = ure.search("(.*?)(\?|$)", url).group(1)
    if '?' in url:
        try:
            for keyvalue in url.split('?')[1].split('&'):
                parameters[unquote(keyvalue.split('=')[0])] = unquote(keyvalue.split('=')[1])
        except IndexError:
            pass
    return path, parameters
