"""
This code tests the PDFVerifier class.
"""

# Standard imports.
from pathlib import Path

# Source imports.
from source.configs import (
    TEST_PATH_TO_DATA,
    TEST_PATH_TO_EXTRACTS,
    TEST_PATH_TO_LEDGER,
    TEST_PATH_TO_PUBLIC_KEY,
    TEST_PATH_TO_PRIVATE_KEY
)
from source.extractor import Extractor
from source.pdf_verifier import PDFVerifier
from source.utils import remove_data_dir

# Local imports.
from utils import construct_test_data

# Local constants.
BAD_PDF_FN = "test_pdf_bad.pdf"
GOOD_PDF_FN = "test_pdf_good.pdf"

###########
# TESTING #
###########

def print_key_from_path(path_to):
    with open(path_to, "r") as key_file:
        key_string = key_file.read()
    print("Key at path: "+path_to)
    print(key_string)

def test_pdf_verifier():
    """ (1) Create a PDF with a bad stamp; (2) create a PDF with a good stamp;
    (3) clean. """
    ordinal = 1
    # Create a PDF with a GOOD stamp.
    path_to_extracted_pdf = \
        str(Path(TEST_PATH_TO_EXTRACTS)/str(ordinal)/"main.pdf")
    construct_test_data()
    extractor = \
        Extractor(
            ordinal=ordinal,
            path_to_extracts=TEST_PATH_TO_EXTRACTS,
            path_to_ledger=TEST_PATH_TO_LEDGER,
            path_to_public_key=TEST_PATH_TO_PUBLIC_KEY
        )
    extractor.extract()
    Path(path_to_extracted_pdf).rename(GOOD_PDF_FN)
    # Test PDFVerifier class.
    pdf_verifier = \
        PDFVerifier(
            path_to_pdf=GOOD_PDF_FN,
            path_to_public_key=TEST_PATH_TO_PUBLIC_KEY
        )
    assert pdf_verifier.verify()
    # Clean.
    remove_data_dir(path_to_data=TEST_PATH_TO_DATA)
    Path(GOOD_PDF_FN).unlink()
