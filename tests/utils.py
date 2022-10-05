"""
This code defines some utilities functions used by multiple test modules.
"""

# Source imports.
from source.configs import (
    TEST_LEDGER_FN,
    TEST_PASSWORD,
    TEST_PATH_TO_DATA,
    TEST_PATH_TO_LEDGER,
    TEST_PATH_TO_PRIVATE_KEY,
    TEST_PATH_TO_PUBLIC_KEY
)
from source.digistamp import generate_keys
from source.ordinance import Ordinance
from source.uploader import Uploader
from source.utils import create_data_dir_as_necessary, remove_data_dir

#############
# FUNCTIONS #
#############

def construct_test_data():
    """ (1) Remove any existing temporary test data. (2) Create the data
    directory. (3) Add test keys. (4) Add test data to the ledger. """
    # Remove existing temporary test data.
    remove_data_dir(path_to_data=TEST_PATH_TO_DATA)
    # Create the data directory.
    create_data_dir_as_necessary(
        path_to_data=TEST_PATH_TO_DATA,
        ledger_fn=TEST_LEDGER_FN
    )
    # Add test keys.
    generate_keys(
        path_to_private_key=TEST_PATH_TO_PRIVATE_KEY,
        path_to_public_key=TEST_PATH_TO_PUBLIC_KEY,
        password=TEST_PASSWORD
    )
    # Add test data to the ledger.
    ordinance = \
        Ordinance(
            ordinance_type="declaration",
            latex="This is a test!",
            year=2000,
            month_num=1,
            day=1,
        )
    uploader = \
        Uploader(
            ordinance=ordinance,
            path_to_private_key=TEST_PATH_TO_PRIVATE_KEY,
            path_to_ledger=TEST_PATH_TO_LEDGER,
            password=TEST_PASSWORD
        )
    uploader.upload()
