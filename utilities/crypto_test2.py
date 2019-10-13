

# A 128 bit (16 byte) key
key = "aaaaaaaaaaaaaaaa"

# For some modes of operation we need a random initialization vector
# of 16 bytes
iv = "InitializationVe"

from crypto_aes import Aes
aes = Aes(key, iv = iv)
plaintext = "TextMustBeXXByte"
ciphertext = aes.encrypt(plaintext)

# '\xd6:\x18\xe6\xb1\xb3\xc3\xdc\x87\xdf\xa7|\x08{k\xb6'
#print (ciphertext)


# The cipher-block chaining mode of operation maintains state, so 
# decryption requires a new instance be created
aes = Aes(key, iv = iv)
decrypted = aes.decrypt(ciphertext)

# True
print(plaintext)
print(str(decrypted))
#print (decrypted == plaintext)
