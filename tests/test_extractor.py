"""
This code tests the Extractor class.
"""

# Source imports.
from source.configs import (
    TEST_PATH_TO_DATA,
    TEST_PATH_TO_EXTRACTS,
    TEST_PATH_TO_LEDGER,
    TEST_PATH_TO_PUBLIC_KEY
)
from source.extractor import Extractor
from source.utils import remove_data_dir

# Local imports.
from utils import construct_test_data

###########
# TESTING #
###########

def test_extractor():
    """ (1) Set up; (2) extract first ordinance; (3) check extract exists; (4)
    clean. """
    # Set up.
    construct_test_data()
    # Extract first ordinance.
    extractor = \
        Extractor(
            ordinal=1,
            path_to_extracts=TEST_PATH_TO_EXTRACTS,
            path_to_ledger=TEST_PATH_TO_LEDGER,
            path_to_public_key=TEST_PATH_TO_PUBLIC_KEY
        )
    extractor.extract()
    # Check extract exists.
    path_obj_to_pdf = extractor.path_obj_to_extract/"main.pdf"
    assert path_obj_to_pdf.exists()
    # Clean.
    remove_data_dir(path_to_data=TEST_PATH_TO_DATA)
