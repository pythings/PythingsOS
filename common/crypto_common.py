
# Imports

import os
try:import base64
except: pass


# Utilities

def bit_length(n):
    res = n
    count = 1
    while res>1:
        res = res>>1
        count = count+1
    return count

def split_text( text, n ):
    while text:
        yield text[:n]
        text = text[n:]

def generate_int_key(size):
    key_str = ''
    for _ in range(0,size):
        b = os.urandom(4)
        key_str += str(bytes_to_int(b) % 2)   
    return bstr_to_int(key_str)


#  Representation/conversions

def int_to_bytes(n):
    try:
        return n.to_bytes((bit_length(n) + 7) // 8, 'big') or b'\0' # Py 3
    except AttributeError:
        import struct
        return struct.pack(">L", n).replace(b'\x00','') # Py 2 (compatibility mode required)

def bytes_to_int(b):
    try:
        import ustruct
        return ustruct.unpack(">i", b)[0] # uPy
    except:
        try:
            return int.from_bytes(b, byteorder='big', signed=False) # Py 3
        except:
            return int(b.encode('hex'), 16) # Py 2

def str_to_int(text):
    text_as_bytes = bytes(text, 'utf-8')    
    text_as_integer = bytes_to_int(text_as_bytes)
    return text_as_integer

def int_to_b64(item):    
    b64_str = base64.b64encode(int_to_bytes(item)).decode('utf-8')
    if b64_str[-2:] != '==':
        b64_str = b64_str + '&&'
    else:
        b64_str = b64_str[:-2]  
    return b64_str       

def b64_to_int(item):    
    b64_bytes = base64.b64decode(item)
    b64_int = bytes_to_int(b64_bytes)
    return b64_int

def str_to_bytes(string):
    try:
        return bytes(string, 'utf-8') # Py 3
    except TypeError:
        return bytes(string) # Py 2

def bstr_to_int(string):
    return int(string, 2)

