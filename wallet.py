from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
# from cryptography.fernet import Fernet
import Crypto.Random
import binascii

class Wallet:

    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key


    def save_keys(self):
        if self.public_key is not None and self.private_key is not None:
            try:
                with open('wallet.txt', mode='w') as f:
                    f.write(self.public_key)
                    f.write("\n")
                    f.write(self.private_key)
            except (IOError, IndexError):
                print('saving wallet failed')
        else:
            print("Keys have not been generated")

    def load_keys(self):
        try:
            with open('wallet.txt', mode='r') as f:
                keys = f.readlines()
                public_key = keys[0][:-1]
                print("I LITERALLY GOT THIS public_key FROM THE FILE! :: ",public_key)
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key        
        except(IOError, IndexError):
            print('Loading wallet failed')

            # f.read(public_key)
            # f.write("\n")
            # f.write(private_key)

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), 
                binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))


    def sign_transaction(self, sender, recipient, amount):
        signer = pkcs1_15.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new( (str(sender) + str(recipient)+ str(amount)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction( transaction):

        
        public_key = RSA.import_key(binascii.unhexlify(transaction.sender))
        h = SHA256.new( (str(transaction.sender) + str(transaction.recipient)+ str(transaction.amount)).encode('utf8'))
        try:
            verifier = pkcs1_15.new(public_key)
            verifier.verify(h, binascii.unhexlify(transaction.signature))

            return True
        except (ValueError, TypeError):
            return False



