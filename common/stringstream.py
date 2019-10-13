data = b''

def clear():
    global data
    data = b''

def read(n=-1):
    return 0

def write(b):
    global data
    data += b
    return len(b)

def close():
    global data
    del data
