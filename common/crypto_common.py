from crypto_aes_128_cbc import Aes128engine

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

try:
    import base64
except:
    pass
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
import os
def generate_int_key(size):
    key_str = ''
    for _ in range(0,size):
        b = os.urandom(4)
        key_str += str(bytes_to_int(b) % 2)   
    return bstr_to_int(key_str)

def generate_aes128_key():
    return generate_int_key(128)


#  Encryption

class Aes128CBC():

    def __init__(self, key, comp_mode=False):
        self.aes = Aes128engine(key)
        self.comp_mode = comp_mode
        self.chunk_int = 39
        self.chunk_b64 = 22
        self.chunk_txt = 12 if self.comp_mode else 16
        
    def encrypt_text_stream(self, text):
        for chunk in split_text(text,self.chunk_txt):
            while len(chunk) < self.chunk_txt:
                chunk+='&'
            print ('chunk lenght:', len(chunk))  
            # Get integer for this chunk starting from 4-bytes sub_chunks for extra-compatibility
            if self.comp_mode:
                chunk_as_integer = 0
                for i, sub_chunk in enumerate(split_text(chunk,4)):
                    
                    #print(sub_chunk, i+1) 
                    print('EN: Sub-string: ', sub_chunk)
                    # Convert to bytes
                    sub_chunk_as_bytes = str_to_bytes(sub_chunk)
                    
                    # Convert to int
                    
                    sub_chunk_as_integer = bytes_to_int(sub_chunk_as_bytes)
                    #print('sub_chunk_as_integer', sub_chunk_as_integer)
                    
                    sub_chunk_as_integer = sub_chunk_as_integer*pow(100000000000,i)
                    #print('sub_chunk_as_integer', sub_chunk_as_integer)
                    
                    chunk_as_integer+=sub_chunk_as_integer
                    
                    #print('total_int',chunk_as_integer)
                    
                    #print('shunk_as_integer_len',len(str(chunk_as_integer)))
                    
            else:
             
            
                # Convert to bytes
                chunk_as_bytes = str_to_bytes(chunk)
                
                # Convert to int
                chunk_as_integer = bytes_to_int(chunk_as_bytes)
                print('chunk_as_integer_len', len(str(chunk_as_integer)))
            
            print('EN: Integer: ', chunk_as_integer)

            # Encrypt integer
            chunk_encrypted = self.aes.encrypt(chunk_as_integer)
            print('EN: Encrypted: ', chunk_encrypted)
            
            if not self.comp_mode:
                # Convert to base64
                chunk_encrypted = int_to_b64(chunk_encrypted)
            else:
                chunk_encrypted = str(chunk_encrypted)
                while len(chunk_encrypted) < self.chunk_int:
                    chunk_encrypted+='&'
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

        print('Using chunksize', chunksize)
        for string in split_text(text,chunksize):
            print('DE: Encrypted: ', string)
            
            if  not self.comp_mode:
                if '&' in string: 
                    string = string.replace('&','')
                else:
                    string = string+'=='
                encrypted_int = b64_to_int(string)
            else:
                string = string.replace('&','')
                encrypted_int = int(string)
                
            print('DE: EncryptedInt: {} {}'.format(encrypted_int, type(encrypted_int)))
            decrypted = self.aes.decrypt(encrypted_int)
            print('DE: Integer: ', decrypted)
            
            if self.comp_mode:
                decrypted_str_chunk = str(decrypted)
                while len(decrypted_str_chunk) < 32:
                    decrypted_str_chunk = '0' + decrypted_str_chunk

                # For each sub int, decryp it:
                decrypted_str = ''
                for i, sub_chunk in enumerate(split_text(decrypted_str_chunk,11)):
                    
                    # Remove middle zeroes
                    if i != 2 :
                        sub_chunk = sub_chunk[:-1]
                    sub_chunk = int(sub_chunk)
                    
                    
                    decrypted_as_bytes = sub_chunk.to_bytes((bit_length(sub_chunk) + 7) // 8, 'big') or b'\0'
                    decrypted_str_sub = decrypted_as_bytes.decode('utf-8').replace('&','')

                    try:
                        import ustruct # detecs uPy
                    except:
                        pass
                    else:
                        decrypted_str_sub = ''.join(reversed(decrypted_str_sub))
                    
                    print('DE: Sub-string: ', decrypted_str_sub)
                    decrypted_str = decrypted_str_sub + decrypted_str
                    
                yield decrypted_str
                    
            else:           
            
                decrypted_as_bytes = decrypted.to_bytes((bit_length(decrypted) + 7) // 8, 'big') or b'\0'
                #logger.info(decrypted_as_bytes)
                decrypted_str = decrypted_as_bytes.decode('utf-8').replace('&','')
                try:
                    import ustruct # detecs uPy
                except:
                    yield decrypted_str
                else:
                    yield ''.join(reversed(decrypted_str))

    def decrypt_text(self, text):
        decrypted_text = ''
        for chunk in self.decrypt_text_stream(text):
            decrypted_text += chunk
        return decrypted_text


    def decrypt_int(self, integer):
        return self.aes.decrypt(integer)  


    





