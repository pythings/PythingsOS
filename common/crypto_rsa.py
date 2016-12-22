
from crypto_common import *

# Home-made debugging switch. TODO: use a proper logger.
debug = False

# Pow implementation for correct modulus handling

def pow3(x, y, z):
    ans = 1
    while y:
        if y & 1:
            ans = (ans * x) % z
        y >>= 1
        if not y:
            break
        x = (x * x) % z
    return ans


# Main Simple RSA class

class Srsa(object):
    
    def __init__(self, pubkey, privkey=None):
        self.pubkey  = pubkey
        self.privkey = privkey

    def encrypt_text(self, text):
        chunks = []
        for chunk in split_text(text,4):
            if debug: print('RSA encrypt: encrypting chunk = ', chunk)
            
            chunk_as_bytes = str_to_bytes(chunk)
            if debug: print('RSA encrypt: chunk_as_bytes = ',chunk_as_bytes)
            
            chunk_as_integer = bytes_to_int(chunk_as_bytes)
            if debug: print('RSA encrypt: chunk_as_integer = ',chunk_as_integer)

            chunk_encrypted = pow3(chunk_as_integer, 65537, self.pubkey)
            if debug: print('RSA: encrypted chunk = ', chunk_encrypted)
            
            chunks.append(chunk_encrypted)

        return chunks

    def decrypt_text(self, chunks):
        message=''
        for chunk in chunks:
            
            if debug: print('RSA decrypt: decrypting chunk = ', chunk)
            
            chunk_decrypted = pow3(chunk, self.privkey, self.pubkey)
            if debug: print ('RSA decrypt: chunk as integer = ',chunk_decrypted)
            
            chunk_as_bytes = int_to_bytes(chunk_decrypted)
            if debug: print ('RSA decrypt: chunk as bytes = ',chunk_as_bytes)
    
            chunk_as_string = chunk_as_bytes.decode('utf-8')
            if debug: print('RSA decrypt: decrypted chunk = ', chunk_as_string)
            
            message += chunk_as_string
            
        return message

