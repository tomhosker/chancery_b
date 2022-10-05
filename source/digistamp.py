"""
This code defines two classes: one of which produces a digital stamp for
documents issued by the Chancellor of Cyprus, and the other of which verfies
the same.
"""

# Standard imports.
import getpass
import os

# Non-standard imports.
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# Local imports.
from .configs import (
    DEFAULT_PATH_TO_PRIVATE_KEY,
    DEFAULT_PATH_TO_PUBLIC_KEY,
    ENCODING
)

# Local constants.
PUBLIC_EXPONENT = 65537
KEY_SIZE = 2048

################
# MAIN CLASSES #
################

class StampMachine:
    """ A class which produces a string of binary, which in turn testifies to
    the authenticity of a given document. """
    def __init__(
            self,
            path_to_private_key=DEFAULT_PATH_TO_PRIVATE_KEY,
            password=None
        ):
        self.private_key = \
            load_private_key(
                path_to_private_key=path_to_private_key,
                password=password
            )
        self.sig = \
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            )

    def make_stamp(self, data):
        """ Ronseal. """
        data_bytes = bytes(data, ENCODING)
        stamp_bytes = \
            self.private_key.sign(data_bytes, self.sig, hashes.SHA256())
        result = stamp_bytes.hex()
        return result

class Verifier:
    """ A class which allows the user to verify a stamp produced as above. """
    def __init__(self, path_to_public_key=DEFAULT_PATH_TO_PUBLIC_KEY):
        self.public_key = \
            load_public_key(path_to_public_key=path_to_public_key)
        self.sig = \
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            )

    def verify(self, data, stamp):
        """ Decide whether the stamp in question is authentic or not. """
        stamp_bytes = bytes.fromhex(stamp)
        data_bytes = bytes(data, ENCODING)
        try:
            self.public_key.verify(
                stamp_bytes,
                data_bytes,
                self.sig,
                hashes.SHA256()
            )
        except InvalidSignature:
            return False
        return True

################################
# HELPER CLASSES AND FUNCTIONS #
################################

class DigistampKeyFileError(Exception):
    """ A custom exception. """

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
        print("Passwords do not match.")
        return get_bytes_password_new()
    result = bytes(password, ENCODING)
    return result

def generate_public_key(
        private_key, path_to_public_key=DEFAULT_PATH_TO_PUBLIC_KEY
    ):
    """ Generate a public key from a private key object. """
    public_key = private_key.public_key()
    pem = \
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    with open(path_to_public_key, "wb") as public_key_file:
        public_key_file.write(pem)

def generate_keys(
        path_to_private_key=DEFAULT_PATH_TO_PRIVATE_KEY,
        path_to_public_key=DEFAULT_PATH_TO_PUBLIC_KEY,
        password=None
    ):
    """ Generate a new private and public key. """
    if os.path.exists(path_to_private_key):
        raise DigistampKeyFileError(
            "Private file already exists at path: "+path_to_private_key
        )
    if password:
        password = bytes(password, ENCODING)
    else:
        password = get_bytes_password_new()
    algorithm = serialization.BestAvailableEncryption(password)
    private_key = \
        rsa.generate_private_key(
            public_exponent=PUBLIC_EXPONENT,
            key_size=KEY_SIZE,
            backend=default_backend()
        )
    pem = \
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=algorithm
        )
    with open(path_to_private_key, "wb") as private_key_file:
        private_key_file.write(pem)
    generate_public_key(private_key, path_to_public_key)

def load_private_key(
        path_to_private_key=DEFAULT_PATH_TO_PRIVATE_KEY,
        password=None
    ):
    """ Load the private key from its file. """
    if not path_to_private_key:
        raise DigistampKeyFileError("No file at path: "+path_to_private_key)
    if password:
        password = bytes(password, ENCODING)
    else:
        password = get_bytes_password()
    with open(path_to_private_key, "rb") as key_file:
        result = \
            serialization.load_pem_private_key(
                key_file.read(),
                backend=default_backend(),
                password=password
            )
    return result

def load_public_key(path_to_public_key=DEFAULT_PATH_TO_PUBLIC_KEY):
    """ Load the public key from its file. """
    if not path_to_public_key:
        raise DigistampKeyFileError("No file at path: "+path_to_public_key)
    with open(path_to_public_key, "rb") as key_file:
        result = \
            serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
    return result

def generate_public_key_from_path(
        path_to_private_key=DEFAULT_PATH_TO_PRIVATE_KEY,
        path_to_public_key=DEFAULT_PATH_TO_PUBLIC_KEY,
        password=None
    ):
    """ Generate a file containing a public key from a path to a file
    containing the private key. """
    private_key = load_private_key(path_to_private_key, password=password)
    generate_public_key(private_key, path_to_public_key=path_to_public_key)
