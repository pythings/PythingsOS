import random

def gen_prime(N=10**8, bases=range(2,20000)):
    # XXX replace with a more sophisticated algorithm
    p = 2
    while any(pow(base, p-1, p) != 1 for base in bases):
        p = random.SystemRandom().randrange(N)
    return p

def multinv(modulus, value):
    '''Multiplicative inverse in a given modulus

        >>> multinv(191, 138)
        18
        >>> 18 * 138 % 191
        1

    '''
    # http://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
    x, lastx = 0, 1
    a, b = modulus, value
    while b:
        a, q, b = b, a // b, a % b
        x, lastx = lastx - q * x, x
    result = (1 - lastx * modulus) // value
    return result + modulus if result < 0 else result

def keygen(N):
    '''Generate public and private keys from primes up to N.

        >>> pubkey, privkey = keygen(2**64)
        >>> msg = 123456789012345
        >>> coded = pow(msg, 65537, pubkey)
        >>> plain = pow(coded, privkey, pubkey)
        >>> assert msg == plain

    '''
    # http://en.wikipedia.org/wiki/RSA
    prime1 = gen_prime(N)
    prime2 = gen_prime(N)
    totient = (prime1 - 1) * (prime2 - 1)
    return prime1 * prime2, multinv(totient, 65537)

print('Starting')
size=0
while size != 1024:
    pubkey, privkey = keygen(2**512) #2**512 for 1024 bits (more or less).  2**64 for 128 bits
    print ('pubkey', str(pubkey))
    print ('privkey', str(privkey))
    size = len(str(bin(pubkey)))
    print ('pubkey bits:', size)
    msg = 123456789012345
    coded = pow(msg, 65537, pubkey)
    plain = pow(coded, privkey, pubkey)
    assert msg == plain


