 
 
# RSA 1024 and AES 128 

# Encrypt
from crypto_common import Aes128CBC, generate_aes128_key


# Init text
text = 'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?'
#smalltext = 'ciao come va in questa mattinatai di giornata di primavera? Pioverà? verrà il sole? Nuvoloni? mah.'
text = 'Ciao come va in questa mattinata di primavera? Piovera? verra il sole? Nuvoloni? mah.'
#smalltext = 'ciao come va in questa mattinata?'

#with open('dante.txt') as f:
#    hugetext = ''.join(f.readlines())


key = generate_aes128_key()
#key = 555555557272723723723971912 
aes128CBC = Aes128CBC(key, comp_mode=True)

#for text in [smalltext, longtext, hugetext]:

# Encryot in 16-bytes (128 bits) chunks using AES ECB (Weak!)

print('\n----------------------')
print('Source: "{}"'.format(text))
print('----------------------')

encrypted = aes128CBC.encrypt_text(text)
print('\n----------------------')
print('Encrypted:"{}"'.format(encrypted))
print('----------------------')

decrypted = aes128CBC.decrypt_text(encrypted)
print('\n----------------------')
print('Decrypted"{}"'.format(decrypted))
print('----------------------')

print('\n----------------------')
print(type(decrypted),type(text))
print(len(decrypted),len(text))
print(decrypted==text)
print('----------------------')


##--------OLD-----------
# Set up master key
#master_key = 0x2b7e151628aed2a6abf7158809cf4f3c #
#master_key = 57811460909138771071931939740208549692 #
#print('master_key', master_key)
#print('Key lengt in bytes', round(len(str(master_key))*3.333/8))
#print('Key lengt in bits', round(len(str(master_key))*3.333/8)*8)
#import sys
#sys.exit(0)
#
#AESC = AES(master_key)
#plaintext = 0x3243f6a8885a308d313198a2e0370734
#plaintext = ''
#encrypted = AESC.encrypt(plaintext)
#print(encrypted)
#print(encrypted == 0x3925841d02dc09fbdc118597196a0b32)




