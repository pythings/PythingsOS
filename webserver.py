
import ure
from common import unquote

#---------------------
# Web server functions
#---------------------
class Sender(object):
    
    def __init__(self, cl):
        self.text_to_send = ''
        self.cl = cl
         
    def send(self, text, last=False):  
        self.cl.write(text)       

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

#---------------------
# Web page config function
#---------------------

def header():
    html = """<!DOCTYPE html>
    <html>
        <head> <title>Pythings Wifi setup</title> </head>
        <body> <center><h1>Pythings Wifi setup</h1></center>"""
    return(html)
       
def footer():
    html="""
        </body>
    </html>
    """
    return(html)


