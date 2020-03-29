"""
This code defines two classes: one of which produces a digital stamp for
documents issued by the Chancellor of Cyprus, and the other of which verfies
the same.
"""

# Standard imports.
import getpass
import os
from pathlib import Path

# Non-standard imports.
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# Local constants.
PATH_TO_DIGISTAMP = str(Path.home())+"/chancery-b/digistamp/"
PATH_TO_PRIVATE_KEY = PATH_TO_DIGISTAMP+"stamp_private_key.pem"
PATH_TO_PUBLIC_KEY = PATH_TO_DIGISTAMP+"stamp_public_key.pem"
PUBLIC_EXPONENT = 65537
KEY_SIZE = 2048
ENCODING = "utf-8"

################
# MAIN CLASSES #
################

class StampMachine:
    """ A class which produces a string which testifies as to the
        authenticity of a given document. """
    def __init__(self, data):
        if not os.path.exists(PATH_TO_PRIVATE_KEY):
            raise Exception("No private key on disk.")
        self.private_key = load_private_key()
        self.data = data

    def make_stamp(self):
        """ Ronseal. """
        data_bytes = bytes(self.data, ENCODING)
        result_bytes = self.private_key.sign(
            data_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH),
                        hashes.SHA256())
        result = result_bytes.hex()
        return result

class Verifier:
    """ A class which allows the user to verify a stamp produced as
    above. """
    def __init__(self, stamp, data):
        self.stamp_str = stamp
        self.stamp_bytes = bytes.fromhex(stamp)
        self.public_key = load_public_key()
        self.data = data

    def verify(self):
        """ Decide whether the stamp in question is authentic or not. """
        data_bytes = bytes(self.data, ENCODING)
        try:
            self.public_key.verify(
                self.stamp_bytes,
                data_bytes,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256())
        except InvalidSignature:
            return False
        else:
            return True

####################
# HELPER FUNCTIONS #
####################

def get_bytes_password():
    """ Get a password from the user, and convert it into bytes. """
    password = getpass.getpass(prompt="Digistamp password: ")
    result = bytes(password, ENCODING)
    return result

def get_bytes_password_new():
    """ Get a NEW password from the user, and convert it into bytes. """
    password = getpass.getpass(prompt="Digistamp password: ")
    password_ = getpass.getpass(prompt="Confirm password: ")
    if password != password_:
        raise Exception("Passwords do not match.")
    result = bytes(password, ENCODING)
    return result

def generate_public_key(private_key):
    """ Generate a public key from a private key object. """
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        ENCODING=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    public_key_file = open(PATH_TO_PUBLIC_KEY, "wb")
    public_key_file.write(pem)
    public_key_file.close()

def generate_keys():
    """ Generate a new private and public key. """
    if os.path.exists(PATH_TO_PRIVATE_KEY):
        raise Exception("Private key file already exists.")
    bpw = get_bytes_password_new()
    private_key = rsa.generate_private_key(public_exponent=PUBLIC_EXPONENT,
                                           key_size=KEY_SIZE,
                                           backend=default_backend())
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(bpw))
    private_key_file = open(PATH_TO_PRIVATE_KEY, "wb")
    private_key_file.write(pem)
    private_key_file.close()
    generate_public_key(private_key)

def load_private_key():
    """ Load the private key from its file. """
    bpw = get_bytes_password()
    key_file = open(PATH_TO_PRIVATE_KEY, "rb")
    result = serialization.load_pem_private_key(key_file.read(),
                                                password=bpw,
                                                backend=default_backend())
    return result

def load_public_key():
    """ Load the public key from its file. """
    key_file = open(PATH_TO_PUBLIC_KEY, "rb")
    result = serialization.load_pem_public_key(key_file.read(),
                                               backend=default_backend())
    return result

###########
# TESTING #
###########

def test():
    """ Run the unit tests. """
    stamp = StampMachine("123").make_stamp()
    assert Verifier(stamp, "123").verify()
    assert not Verifier(stamp, "abc").verify()
    print("Tests passed!")

###################
# RUN AND WRAP UP #
###################

def run():
    test()

if __name__ == "__main__":
    run()
