""" This code reads a PDF, and either verifies or falsifies it as an
Ordinance issued by the Chancellor. """

# Standard imports.
import hashlib
import os

# Non-standard imports.
from pdfrw import PdfReader

# Local imports.
from digistamp.digistamp import Verifier

# Local constants.
ENCODING = "utf-8"

##############
# MAIN CLASS #
##############

class PDFVerifier:
    """ The class in question. """
    def __init__(self, path_to_pdf):
        self.trailer = PdfReader(path_to_pdf)
        self.data = None
        self.hash = None
        self.stamp = None

    def load_data(self):
        """ Load the Ordinance's data from the trailer. """
        self.data = Metadata()
        if not self.data.load_from_trailer(self.trailer):
            print("Error loading Ordinance's data from trailer.")
            return False
        return True

    def load_hash(self):
        """ Load the hash from the trailer. """
        if self.trailer.Info.hash is None:
            return False
        a_buffer = self.trailer.Info.hash
        self.hash = a_buffer[1:-1]
        return True

    def load_stamp(self):
        """ Load the stamp from the trailer. """
        if self.trailer.Info.stamp is None:
            return False
        a_buffer = self.trailer.Info.stamp
        self.stamp = a_buffer[1:-1]
        return True

    def check_hash(self):
        """ Check that the hash is what it's supposed to be, given the
        Ordinance's data. """
        hash_maker = hashlib.sha256()
        hash_maker.update(bytes(self.data.ordinal))
        hash_maker.update(bytes(self.data.ordinance_type, ENCODING))
        hash_maker.update(bytes(self.data.latex, ENCODING))
        hash_maker.update(bytes(self.data.year))
        hash_maker.update(bytes(self.data.month))
        hash_maker.update(bytes(self.data.day))
        if self.data.annexe:
            hash_maker.update(self.data.annexe)
        hash_maker.update(bytes(self.data.prev, ENCODING))
        intended_hash = hash_maker.hexdigest()
        if self.hash != intended_hash:
            print("Failed to verify hash.")
            return False
        return True

    def check_stamp(self):
        """ Verify the stamp against the hash. """
        verifier = Verifier(self.stamp, self.hash)
        if not verifier.verify():
            print("Failed to verify stamp.")
            return False
        return True

    def verify(self):
        """ Carry out all the checks. """
        if (self.load_data() and self.load_hash() and self.load_stamp() and
            self.check_hash() and self.check_stamp()):
            print("PDF verified!")
            return True
        print("Failed to verify PDF.")
        return False

################################
# HELPER CLASSES AND FUNCTIONS #
################################

class Metadata:
    """ A helper class to hold a PDF's metadata. """
    def __init__(self):
        self.ordinal = None
        self.ordinance_type = None
        self.latex = None
        self.year = None
        self.month = None
        self.day = None
        self.annexe = None
        self.prev = None

    def load_from_trailer(self, trailer):
        """ Ronseal. """
        try:
            self.annexe = self.load_annexe(trailer.Info.data_annexe)
        except:
            return False
        if trailer.Info.data_ordinal is None:
            return False
        else:
            self.ordinal = int(trailer.Info.data_ordinal)
        if trailer.Info.data_ordinanceType is None:
            return False
        else:
            a_buffer = str(trailer.Info.data_ordinanceType)
            a_buffer = a_buffer[1:-1]
            self.ordinance_type = a_buffer
        if trailer.Info.data_latex is None:
            return False
        else:
            a_buffer = str(trailer.Info.data_latex)
            a_buffer = a_buffer[1:-1]
            self.latex = a_buffer
        if trailer.Info.data_year is None:
            return False
        else:
            self.year = int(trailer.Info.data_year)
        if trailer.Info.data_month is None:
            return False
        else:
            self.month = int(trailer.Info.data_month)
        if trailer.Info.data_day is None:
            return False
        else:
            self.day = int(trailer.Info.data_day)
        if trailer.Info.data_prev is None:
            return False
        else:
            a_buffer = str(trailer.Info.data_prev)
            a_buffer = a_buffer[1:-1]
            self.prev = a_buffer
        return True

    def load_annexe(self, annexe_raw):
        """ Do the special stuff necessary to load the annexe's bytes. """
        a_buffer = str(annexe_raw)
        a_buffer = a_buffer[1:-1]
        result = bytes.fromhex(a_buffer)
        return result

def pick_the_first_path(dir_name):
    """ A function which picks the first file in a given directory. """
    if not dir_name.endswith("/"):
        dir_name = dir_name+"/"
    paths = os.listdir(dir_name)
    if len(paths) == 0:
        raise Exception("No file in "+dir_name+" for me to pick.")
    elif len(paths) > 1:
        print("More than one file. Picking the first.")
    result = dir_name+paths[0]
    return result

###########
# TESTING #
###########

def test():
    """ Run the unit tests. """
    verifier = PDFVerifier("test_files/bad_metadata.pdf")
    assert not verifier.verify()
    verifier = PDFVerifier("test_files/good_metadata.pdf")
    assert verifier.verify()
    print("Tests passed!")

###################
# RUN AND WRAP UP #
###################

def verify_first_path():
    """ Verify the first path in a given directory. """
    path_to = pick_the_first_path("pdf_to_verify/")
    verifier = PDFVerifier(path_to)
    verifier.verify()

def run():
    #test()
    verify_first_path()

if __name__ == "__main__":
    run()
