### This code defines two classes: one of which produces a digital stamp for
### documents issued by the Chancellor of Cyprus, and the other of which
### verfies the same.

# Imports.
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from pathlib import Path
import datetime, getpass, os

# Local constants.
path_to_digistamp = str(Path.home())+"/chancery-b/digistamp/"
path_to_private_key = path_to_digistamp+"stamp_private_key.pem"
path_to_public_key = path_to_digistamp+"stamp_public_key.pem"
public_exponent = 65537
key_size = 2048
encoding = "utf-8"

################
# MAIN CLASSES #
################

# A class which produces a string which testifies as to the authenticity of
# a given document.
class Stamp_Machine:
    def __init__(self, data):
        if os.path.exists(path_to_private_key) == False:
            raise Exception("No private key on disk.")
        self.private_key = load_private_key()
        self.data = data

    # Ronseal.
    def make_stamp(self):
        data_bytes = bytes(self.data, encoding)
        result_bytes = self.private_key.sign(
                           data_bytes,
                           padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                       salt_length=padding.PSS.MAX_LENGTH),
                           hashes.SHA256())
        result = result_bytes.hex()
        return result

# A class which allows the user to verify a stamp produced as above.
class Verifier:
    def __init__(self, stamp, data):
        if isinstance(stamp, str) == False:
            raise Exception("")
        self.stamp_str = stamp
        self.stamp_bytes = bytes.fromhex(stamp)
        self.public_key = load_public_key()
        self.data = data

    # Decide whether the stamp in question is authentic or not.
    def verify(self):
        data_bytes = bytes(self.data, encoding)
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

# Get a password from the user, and convert it into bytes.
def get_bytes_password():
    password = getpass.getpass(prompt="Digistamp password: ")
    result = bytes(password, encoding)
    return result

# Get a NEW password from the user, and convert it into bytes.
def get_bytes_password_new():
    password = getpass.getpass(prompt="Digistamp password: ")
    password_ = getpass.getpass(prompt="Confirm password: ")
    if password != password_:
        raise Exception("Passwords do not match.")
    result = bytes(password, encoding)
    return result

# Generate a public key from a private key object.
def generate_public_key(private_key):
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
              encoding=serialization.Encoding.PEM,
              format=serialization.PublicFormat.SubjectPublicKeyInfo)
    f = open(path_to_public_key, "wb")
    f.write(pem)
    f.close()

# Generate a new private and public key.
def generate_keys():
    if os.path.exists(path_to_private_key):
        raise Exception("Private key file already exists.")
    bpw = get_bytes_password_new()
    private_key = rsa.generate_private_key(public_exponent=public_exponent,
                                           key_size=key_size,
                                           backend=default_backend())
    pem = private_key.private_bytes(
              encoding=serialization.Encoding.PEM,
              format=serialization.PrivateFormat.PKCS8,
              encryption_algorithm=
                  serialization.BestAvailableEncryption(bpw))
    f = open(path_to_private_key, "wb")
    f.write(pem)
    f.close()
    generate_public_key(private_key)

# Load the private key from its file.
def load_private_key():
    bpw = get_bytes_password()
    key_file = open(path_to_private_key, "rb")
    result = serialization.load_pem_private_key(key_file.read(),
                                                password=bpw,
                                                backend=default_backend())
    return result

# Load the public key from its file.
def load_public_key():
    key_file = open(path_to_public_key, "rb")
    result = serialization.load_pem_public_key(key_file.read(), 
                                               backend=default_backend())
    return result

###########
# TESTING #
###########

# Run the unit tests.
def test():
    stamp = Stamp_Machine("123").make_stamp()
    assert(Verifier(stamp, "123").verify())
    assert(Verifier(stamp, "abc").verify() == False)
    print("Tests passed!")

###################
# RUN AND WRAP UP #
###################

def run():
    test()

if __name__ == "__main__":
    run()
