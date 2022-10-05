"""
This code reads a PDF, and either verifies or falsifies it as an ordinance
issued by the Chancellor.
"""

# Standard imports.
from dataclasses import dataclass

# Non-standard imports.
from pdfrw import PdfReader

# Local imports.
from .configs import DEFAULT_PATH_TO_PUBLIC_KEY
from .digistamp import Verifier
from .ordinance import Ordinance
from .utils import get_hash_of_ordinance

##############
# MAIN CLASS #
##############

@dataclass
class PDFVerifier:
    """ The class in question. """
    # Object attributes.
    path_to_pdf: str = None
    path_to_public_key: str = DEFAULT_PATH_TO_PUBLIC_KEY
    trailer: PdfReader = None
    verifier: Verifier = None
    ordinance: Ordinance = None
    hash: str = None
    stamp: str = None
    last_exception: Exception = None
    debug: bool = True

    def __post_init__(self):
        self.trailer = PdfReader(self.path_to_pdf)
        self.verifier = Verifier(path_to_public_key=self.path_to_public_key)

    def load_ordinance(self):
        """ Load the ordinance's data from the trailer. """
        self.ordinance = Ordinance()
        self.ordinance.load_from_trailer(self.trailer)

    def load_hash(self):
        """ Load the hash from the trailer. """
        if not self.trailer.Info.hash:
            raise PDFVerifierError("Missing hash.")
        my_buffer = self.trailer.Info.hash
        self.hash = my_buffer[1:-1]

    def load_stamp(self):
        """ Load the stamp from the trailer. """
        if not self.trailer.Info.stamp:
            raise PDFVerifierError("Missing stamp.")
        my_buffer = self.trailer.Info.stamp
        self.stamp = my_buffer[1:-1]

    def check_hash(self):
        """ Check that the hash is what it's supposed to be, given the
        ordinance's data. """
        print(self.ordinance.__dict__)
        intended_hash = get_hash_of_ordinance(self.ordinance)

        print("Expected hash: "+str(intended_hash))
        print("Actual hash: "+str(self.hash))

        if self.hash != intended_hash:
            raise PDFVerifierError("Failed to verify hash.")

    def check_stamp(self):
        """ Verify the stamp against the hash. """
        print("PDFVerifier - hash:")
        print(self.hash)
        print("PDFVerifier - stamp:")
        print(self.stamp)

        if not self.verifier.verify(self.hash, self.stamp):
            raise PDFVerifierError("Failed to verify stamp.")

    def verify(self):
        """ Carry out all the checks. """
        try:
            self.load_ordinance()
            self.load_hash()
            self.load_stamp()
            self.check_hash()
            self.check_stamp()
        except PDFVerifierError as my_exception:
            self.last_exception = my_exception
            if self.debug:
                print(my_exception)
            return False
        return True

################
# HELPER CLASS #
################

class PDFVerifierError(Exception):
    """ A custom exception. """
