
from crypto_engine_aes128ecb import Aes128ecb_engine
from crypto_common import *

# Home-made debugging switch. TODO: use a proper logger.
debug = False

class Aes128ecb():

    def __init__(self, key=None, comp_mode=False):
        if not key:
            # print('AES: Generating new key...')
            key = generate_int_key(128)
            # print ('AES: generated key', key)
        else:
            pass
            # print ('AES: initialized with key', key)
               
        self.key = key
        self.aes = Aes128ecb_engine(self.key)
        self.comp_mode = comp_mode
        self.chunk_int = 39
        self.chunk_b64 = 22
        self.chunk_txt = 12 if self.comp_mode else 16
        
    def encrypt_text_stream(self, text):
        for chunk in split_text(text,self.chunk_txt):
            if debug: print('AES encrypt: chunk = ', chunk)
            while len(chunk) < self.chunk_txt:
                chunk+='&'
            # Get integer for this chunk starting from 4-bytes sub_chunks for extra-compatibility
            if self.comp_mode:
                chunk_as_integer = 0
                for i, sub_chunk in enumerate(split_text(chunk,4)):
                    
                    if debug: print('AES encrypt: sub_ckunk = ', sub_chunk)
 
                    sub_chunk_as_bytes = str_to_bytes(sub_chunk)
                    if debug: print('AES encrypt: sub_chunk_as_bytes = ', sub_chunk_as_bytes)
    
                    sub_chunk_as_integer = bytes_to_int(sub_chunk_as_bytes)
                    if debug: print('AES encrypt: sub_chunk_as_integer = ', sub_chunk_as_integer)
                    
                    sub_chunk_as_integer = sub_chunk_as_integer*pow(100000000000,i)
                    if debug: print('AES encrypt: sub_chunk_as_integer (shifted) = ', sub_chunk_as_integer)
                    
                    chunk_as_integer += sub_chunk_as_integer
                    
            else:
             
                chunk_as_bytes = str_to_bytes(chunk)
                if debug: print('AES encrypt: chunk_as_bytes = ', chunk_as_bytes)
                
                chunk_as_integer = bytes_to_int(chunk_as_bytes)
            
            if debug: print('AES encrypt: chunk_as_integer = ', chunk_as_integer)
            chunk_encrypted = self.aes.encrypt(chunk_as_integer)
            if debug: print('AES encrypt: chunk_encrypted = ', chunk_encrypted)
            
            if not self.comp_mode:
                chunk_encrypted = int_to_b64(chunk_encrypted)
            else:
                chunk_encrypted = str(chunk_encrypted)
                while len(chunk_encrypted) < self.chunk_int:
                    chunk_encrypted+='&'
            
            if debug: print('AES encrypt: chunk_encrypted (padded) = ', chunk_encrypted)
            yield chunk_encrypted

    def encrypt_text(self, text):
        encrypted_text = ''
        for chunk in self.encrypt_text_stream(text):
            encrypted_text += chunk
        return encrypted_text

    def encrypt_int(self, integer):
        return self.aes.encrypt(integer)  

    def decrypt_text_stream(self, text):
        if not self.comp_mode:
            chunksize = self.chunk_b64
        else:
            chunksize = self.chunk_int

        #print('Using chunksize', chunksize)
        for chunk in split_text(text,chunksize):
            if debug: print('AES decrypt: chunk = ', chunk)

            if  not self.comp_mode:
                if '&' in chunk: 
                    chunk = chunk.replace('&','')
                else:
                    chunk = chunk+'=='
                chunk_as_int = b64_to_int(chunk)
            else:
                chunk = chunk.replace('&','')
                chunk_as_int = int(chunk)
            
            if debug: print('AES decrypt: chunk_as_int = ', chunk_as_int)
            
            decrypted_chunk = self.aes.decrypt(chunk_as_int)
            if debug: print('AES decrypt: decrypted_chunk = ', decrypted_chunk)
            
            if self.comp_mode:
                decrypted_str_chunk = str(decrypted_chunk)
                while len(decrypted_str_chunk) < 32:
                    decrypted_str_chunk = '0' + decrypted_str_chunk

                # For each sub int, decryp it:
                chunk_decrypted = ''
                for i, sub_chunk in enumerate(split_text(decrypted_str_chunk,11)):
                    
                    # Convert to int and remove middle zeroes
                    if i != 2 :
                        sub_chunk = sub_chunk[:-1]
                    sub_chunk = int(sub_chunk)
                    
                    sub_chunk_as_bytes = int_to_bytes(sub_chunk)
                    if debug: print('AES decrypt: sub_chunk_as_bytes', sub_chunk_as_bytes)
                    
                    sub_chunk_decrypted = sub_chunk_as_bytes.decode('utf-8').replace('&','')
                    if debug: print('AES decrypt: sub_chunk_decrypted = ', sub_chunk_decrypted)
                    
                    chunk_decrypted = sub_chunk_decrypted + chunk_decrypted
                
                if debug: print('AES decrypt: chunk_decrypted = ', chunk_decrypted)  
                yield chunk_decrypted
                    
            else:           
            
                chunk_as_bytes = int_to_bytes(decrypted_chunk)
                if debug: print('AES decrypt: chunk_as_bytes = ', chunk_as_bytes)
                
                chunk_decrypted = chunk_as_bytes.decode('utf-8').replace('&','')
                if debug: print('AES decrypt: chunk_decrypted = ', chunk_decrypted) 
                
                try: import ustruct # detecs uPy
                except: yield chunk_decrypted
                else: yield ''.join(reversed(chunk_decrypted))

    def decrypt_text(self, text):
        decrypted_text = ''
        for chunk in self.decrypt_text_stream(text):
            decrypted_text += chunk
        return decrypted_text

    def decrypt_int(self, integer):
        return self.aes.decrypt(integer) 
