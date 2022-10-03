"""
This code reads a PDF, and either verifies or falsifies it as an ordinance
issued by the Chancellor.
"""

# Standard imports.
import os

# Non-standard imports.
from pdfrw import PdfReader

# Local imports.
from .digistamp import Verifier
from .ordinance import Ordinance
from .utils import get_hash_of_ordinance, raw_to_usable

##############
# MAIN CLASS #
##############

class PDFVerifier:
    """ The class in question. """
    def __init__(self, path_to_pdf):
        self.trailer = PdfReader(path_to_pdf)
        self.ordinance = None
        self.hash = None
        self.stamp = None
        self.last_exception = None

    def load_ordinance(self):
        """ Load the ordinance's data from the trailer. """
        self.ordinance = Ordinance()
        if not self.ordinance.load_from_trailer(self.trailer):
            raise PDFVerifierError("Error loading data from trailer.")

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
        intended_hash = get_hash_of_ordinance(self.ordinance)
        if self.hash != intended_hash:
            raise PDFVerifierError("Failed to verify hash.")

    def check_stamp(self):
        """ Verify the stamp against the hash. """
        verifier = Verifier()
        if not verifier.verify(self.stamp, self.hash):
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
            return False
        return True

################
# HELPER CLASS #
################

class PDFVerifierError(Exception):
    """ A custom exception. """
