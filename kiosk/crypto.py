import base64
import hashlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidSignature



def loadKioskPrivateKey():
    with open("kiosk_private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())
        return private_key

def loadKioskPublicKey():
    with open("kiosk_public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())
        print(public_key)
        return public_key

def loadUserPrivateKey():
    with open("user_private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())
        print(private_key)
        return private_key
        
def loadUserPublicKey():
    with open("user_public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(key_file.read(), backend=RSABackend())
        print(public_key)
        return public_key	

def sign(plaintext):

    private_key = loadKioskPrivateKey()

    sig = private_key.sign(plaintext,
                           padding.PKCS1v15(),
                           hashes.SHA256())

    return sig


def generateAESGCMKey():
    key = AESGCM.generate_key(bit_length=128)
    encoded_key = base64.b64encode(key)
    print(encoded_key)
    with open('AESKey.psk', 'wb') as f:
        f.write(encoded_key)

def loadAESGCMKey():
    with open("AESKey.psk", "rb") as key_file:
        encoded_key = key_file.read()
    return base64.b64decode(encoded_key)


def aeadDecrypt(nonce, ciphertext, aad):
    key = loadAESGCMKey()
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, aad)

def verifySignature(signature, plaintext):
    public_key = loadUserPrivateKey().public_key()
    try:
        public_key.verify(signature,
                    plaintext, padding.PKCS1v15(),
                    hashes.SHA256())
        return True
    except InvalidSignature:
        return False

