"""
This code defines a number of functions which together provide the machine
interface for rest of the codebase.
"""

# Standard imports.
import json

# Local imports.
from .configs import DEFAULT_PATH_TO_PUBLIC_KEY
from .extractor import Extractor
from .ordinance import Ordinance
from .pdf_verifier import PDFVerifier
from .uploader import Uploader

#############
# FUNCTIONS #
#############

def upload_ordinance_from_input_file(path_to_input_file):
    """ Ronseal. """
    with open(path_to_input_file, "r") as input_file:
        input_dict = json.loads(input_file.read())
    ordinance = Ordinance(**input_dict)
    uploader = Uploader(ordinance=ordinance)
    uploader.upload()

def extract_ordinance_with_ordinal(ordinal):
    """ Ronseal. """
    extractor = Extractor(ordinal=ordinal)
    result = extractor.extract()
    return result

def verify_pdf(path_to_pdf, path_to_public_key=DEFAULT_PATH_TO_PUBLIC_KEY):
    """ Ronseal. """
    document_verifier = \
        PDFVerifier(
            path_to_pdf=path_to_pdf,
            path_to_public_key=path_to_public_key
        )
    result = document_verifier.verify()
    return result
