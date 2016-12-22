 
 
# RSA 1024 and AES 128 

# Encrypt
from crypto_aes import Aes128cbc
from crypto_rsa import Srsa


# Init text
text = 'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?'
text = 'Ciao come va in questa mattinata di primavera? Piovera? verra il sole? Nuvoloni? mah.'
#smalltext = 'ciao come va in questa mattinata?'
text = 'Ciao come va'

#with open('dante.txt') as f:
#    hugetext = ''.join(f.readlines())


# Encypt key with Pything's public Key


#rsa_pubkey=90068364852450250136085463497212929703877898534585770340898518991456038104325197679167979847395872742695634771751317027247827314873735124607739473628242487791732089797915636001276502167801886101892767403979587098106248081740356915461723527354061326092801105254986448794568922848908038913584421580879950597547
#rsa_privkey=72358964826683524114851698103235698335884694687649349134361474028703661477193432458090442146348476368702684992713712754651957763636068603166487496009896611267018613709161143371965854195462150524671158966044620524184648712849979442266761237076796886708696623660804584094806404867908654555044784591901949899441

#rsa_pubkey=49148514185808853110502468909594556567190989188823722051706055298326721690635028848337232532257835475471896537195057817433392095017883613984648410043038363007223210712937360371780319582221727112777241645706582542711795830554889946791224695127536188409113979706128013955738193346996398493784033650859069217559
#rsa_privkey=5985234168743464862214019628110443809798301489479257910717091525946344291208907414721141535925504446797094866462513640248041599559603416744914765102972199789430811002340822436071777983676168457745229240792272761513941173865686271732456320337104564228048197773104281215569281890170063535154640333643736001393


with open('pubkey.key') as f:
    rsa_pubkey = int(f.read())

with open('privkey.key') as f:
    rsa_privkey = int(f.read())    
    
print(rsa_pubkey)
print(len(str(bin(rsa_pubkey))))
print(rsa_privkey)
print(len(str(bin(rsa_privkey))))
#import sys
#sys.exit(0)


srsa = Srsa(pubkey=rsa_pubkey, privkey=rsa_privkey)


# Encrypt aes_key key

aes_key = 5734657497481
aes128CBC = Aes128cbc(key=aes_key, comp_mode=True)

aes_key_encrypted = srsa.encrypt_text(str(aes_key))
print('aes_key_encrypted', aes_key_encrypted)
aes_key_decrypted = srsa.decrypt_text(aes_key_encrypted)
print('aes_key_decrypted', aes_key_decrypted)

#key = 555555557272723723723971912 


#for text in [smalltext, longtext, hugetext]:

# Encryot in 16-bytes (128 bits) chunks using AES ECB (Weak!)

print('\n----------------------')
print('Source: "{}"'.format(text))
print('----------------------')

encrypted = aes128CBC.encrypt_text(text)
print('\n----------------------')
print('Encrypted: "{}"'.format(encrypted))
print('Len Encrypted: "{}"'.format(len(encrypted)))
print('----------------------')

decrypted = aes128CBC.decrypt_text(encrypted)
print('\n----------------------')
print('Decrypted: "{}"'.format(decrypted))
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

# Print key
from crypto_common import split_text
pubkey_hex_str = str(hex(rsa_pubkey))
pubkey_hex_str = iter(pubkey_hex_str)
pubkey_hex_str_pretty = ' '.join(a+b for a,b in zip(pubkey_hex_str, pubkey_hex_str))
pubkey_hex_str_pretty = '\n'.join(split_text(pubkey_hex_str_pretty,48))
print(pubkey_hex_str_pretty)







#import sys
#import math
#from crypto_common import int_to_bytes
#print(len(int_to_bytes(rsa_pubkey)))
#print(sys.getsizeof(int_to_bytes(rsa_pubkey)))
#print(  len(str(rsa_pubkey)) * (math.log(10)/math.log(2)))
#print(len(str(bin(rsa_pubkey))))












