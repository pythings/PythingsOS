

DEBUG = 10
INFO = 20
WARNING =  30
ERROR = 40
CRITICAL= 50

level = INFO

def basicConfig(level):
    level = level

loggers = {}

class Logger(object):

    def __init__(self,name):
        self.name=name

    def debug(self,msg):
        if level <= DEBUG: 
            print(self.name+': DEBUG: ' +msg)
            
    def info(self,msg):
        if level <= INFO: 
            print(self.name+': INFO: ' +msg)
            
    def warning(self,msg):
        if level <= WARNING: 
            print(self.name+': WARNING: ' +msg)

    def error(self,msg):
        if level <= ERROR: 
            print(self.name+': ERROR: ' +msg)

    def critical(self,msg):
        if level <= CRITICAL: 
            print(self.name+': CRITICAL: ' +msg)


def getLogger(name):
    if name not in loggers:
        loggers[name] = Logger(name)
    return loggers[name]




