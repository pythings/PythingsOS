import logger
try:
    import base64
    base64 = None 
except:
    base64 = None    
import os
from crypto_aes128 import Aes128engine


# Utilities

def bit_length(n):
    res = n
    count = 1
    while res>1:
        res = res>>1
        count = count+1
    return count

def split_text( text, n ):
    """A generator to divide a sequence into chunks of n units."""
    while text:
        yield text[:n]
        text = text[n:]


#  Representation/conversions

def int_to_bytes(n):
    return n.to_bytes((bit_length(n) + 7) // 8, 'big') or b'\0'

def bytes_to_int(b):
    try:
        import ustruct
        return ustruct.unpack(">i", b)[0]
    except:
        return int.from_bytes(b, byteorder='big', signed=False) # Py

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
    return bytes(string, 'utf-8')

def bstr_to_int(string):
    return int(string, 2)


# Key generation

def generate_int_key(size):
    key_str = ''
    for _ in range(0,size):
        b = os.urandom(4)
        key_str += str(bytes_to_int(b) % 2)
    #while key_str.startswith('0'):
    #    key_str = key_str[1:] + key_str[0]    
    return bstr_to_int(key_str)

def generate_aes128_key():
    return generate_int_key(128)


#  Encryption

class Aes128():

    def __init__(self, key):
        self.aes = Aes128engine(key)
        self.chunk_split = 4 # 16 is the best for Aes128. 4 is the safer.
        self.chunk_int = 39
        self.chunk_b64 = 22
        
    def encrypt_text_stream(self, text):
        for chunk in split_text(text,self.chunk_split):
            print(chunk)
            # Convert to bytes
            chunk_as_bytes = str_to_bytes(chunk)
            
            # Convert to int
            chunk_as_integer = bytes_to_int(chunk_as_bytes)
            logger.info('EN: Integer: ', chunk_as_integer)
            
            # Encrypt integer
            chunk_encrypted = self.aes.encrypt(chunk_as_integer)
            logger.info('EN: Encrypted: ', chunk_encrypted)
            
            if base64:
                # Convert to base64
                chunk_encrypted = int_to_b64(chunk_encrypted)
            else:
                chunk_encrypted = str(chunk_encrypted)
                while len(chunk_encrypted) < self.chunk_int:
                    chunk_encrypted+='&'

            # Add to encrypted text (TODO: yeld)
            yield chunk_encrypted

    def encrypt_text(self, text):
        encrypted_text = ''
        for chunk in self.encrypt_text_stream(text):
            encrypted_text += chunk
        return encrypted_text

    def encrypt_int(self, integer):
        return self.aes.encrypt(integer)  

    
    def decrypt_text_stream(self, text):
        
        if base64:
            chunksize = self.chunk_b64
        else:
            chunksize = self.chunk_int

        logger.info('Using chunksize', chunksize)
        for string in split_text(text,chunksize):
            logger.info('DE: Encrypted: ', string)
            
            if base64:
                if '&' in string: 
                    string = string.replace('&','')
                else:
                    string = string+'=='
                encrypted_int = b64_to_int(string)
            else:
                string = string.replace('&','')
                encrypted_int = int(string)
                
            logger.info('DE: EncryptedInt: {} {}'.format(encrypted_int, type(encrypted_int)))
            decrypted = self.aes.decrypt(encrypted_int)
            logger.info('DE: Integer: ', decrypted)
            
            decrypted_as_bytes = decrypted.to_bytes((bit_length(decrypted) + 7) // 8, 'big') or b'\0'
            logger.info(decrypted_as_bytes)
            decrypted_str = decrypted_as_bytes.decode('utf-8')

            yield decrypted_str


    def decrypt_text(self, text):
        decrypted_text = ''
        for chunk in self.decrypt_text_stream(text):
            decrypted_text += chunk
        return decrypted_text


    def decrypt_int(self, integer):
        return self.aes.decrypt(integer)  


    