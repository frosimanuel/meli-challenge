
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import scrypt
import bcrypt

class Crypto:
    # AES Key Size is 32 bytes or 256 bits.
    AES_KEY_SIZE = 32
   
    # Salt length is 32 bytes.
    SALT_LENGTH = 32

    # Generates a Cryptographically secure random sequence of bytes.
    @classmethod
    def random_bytes(cls, key_size):
        return get_random_bytes(key_size)

    # Encrypts data given an AES key.
    @classmethod
    def encrypt(cls, data, key):
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        nonce = cipher.nonce
        return (ciphertext,tag,nonce)
    
    @classmethod
    def decrypt(cls, ciphertext, nonce, tag, key):
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        return data

    # KDF generating a key given a password and salt.
    @classmethod
    def key_derivation_function(cls, password, salt):
        # argument list being passed into scrypt hash function:
        # arg0 - password
        # arg1 - salt
        # arg2 - iteration count
        # arg3 - block size
        # arg4 - number of threads
        # arg5 - hash size

        return scrypt.hash(password, salt, 2**12, 2**3, 1, 32)   #Para extra seguridad, podríamos recibir alguno de estos valores desde una variable de entorno
    
    # Hash a secret
    @classmethod
    def hash_secret(cls, secret):
        secret_bytes = bytes(secret, 'ascii')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(secret_bytes, salt)
        return hashed
    
    @classmethod
    def verify_secret(cls, secret, hashed):
        return hashed == bcrypt.hashpw(secret, hashed)
    