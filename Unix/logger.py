
DEBUG = 10
INFO = 20
WARNING =  30
ERROR = 40
CRITICAL= 50

level = INFO

def emit(level,msg, det):
        print('{}: '.format(level), end='')
        print(msg, end='')
        print(' ', end='')
        print(det, end='')
        print('')  

def debug(msg,det=''):
    if level <= DEBUG:
        emit('DEBUG',msg,det) 
  
def info(msg,det=''):
    if level <= INFO: 
        emit('INFO',msg,det) 
    
def warning(msg,det=''):
    if level <= WARNING: 
        emit('WARNING',msg,det) 

def error(msg,det=''):
    if level <= ERROR: 
        emit('ERROR',msg,det) 

def critical(msg,det=''):
    if level <= CRITICAL: 
        emit('CRITICAL',msg,det) 




