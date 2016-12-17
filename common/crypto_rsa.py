

#-----------------------------
# Utility functions
#-----------------------------

def bit_length(n):
    res = n
    count = 1
    while res>1:
        res = res>>1
        count = count+1
    return count


def split_text( seq, n ):
    """A generator to divide a sequence into chunks of n units."""
    while seq:
        yield seq[:n]
        seq = seq[n:]

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

#-----------------------------
# Keys
#-----------------------------

pubkey=90068364852450250136085463497212929703877898534585770340898518991456038104325197679167979847395872742695634771751317027247827314873735124607739473628242487791732089797915636001276502167801886101892767403979587098106248081740356915461723527354061326092801105254986448794568922848908038913584421580879950597547



#-----------------------------
# Encode
#-----------------------------
def encrypt(text):
    chunks = []
    for chunk in split_text(text,4):
        print('Encrypting: ', chunk)
        
        # Convert to bytes
        chunk_as_bytes = bytes(chunk, 'utf-8')
        
        # Convert to integer
        try:
            # Micropython
            chunk_as_integer =  int.from_bytes(chunk_as_bytes)
        except:
            # Python
            chunk_as_integer =  int.from_bytes(chunk_as_bytes, byteorder='big', signed=False)
        
        # Encrypt integer
        chunk_encrypted = pow3(chunk_as_integer, 65537, pubkey)
        
        chunks.append(chunk_encrypted)
        
        print('Encrypted: ', chunk_encrypted)
    return chunks

def decrypt(chunks):
    message=''
    for chunk in chunks:
        
        print('Decrypting: ', chunk)
        
        chunk_decrypted = pow3(chunk, privkey, pubkey)
        
        # Convert back integer to bytes
        chunk_as_bytes = chunk_decrypted.to_bytes((bit_length(chunk_decrypted) + 7) // 8, 'big') or b'\0'

        # and now convert back bytes to string
        chunk_as_string = chunk_as_bytes.decode('utf-8')
        
        print('Decrypted: ', chunk_as_string)
        message += chunk_as_string
    return message


#-----------------------------
# Test
#-----------------------------

input_text = 'Today is a very nice day!'
input_text = 'hey'
print('input_text', input_text)
encypted = encrypt(input_text)
print('encypted', encypted)
output_text = decrypt(encypted)
print('output_text', output_text)



























