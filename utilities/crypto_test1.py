from crypto_common import Aes128
key = 555555557272723723723971912 
aes128 = Aes128(key)


for text in ['ciao']:

    # Encryot in 16-bytes (128 bits) chunks using AES
    encrypted = aes128.encrypt_int(132140738950934151784931744258137353760)
    print(encrypted)
    decrypted = aes128.decrypt_int(encrypted)
    print(decrypted)
