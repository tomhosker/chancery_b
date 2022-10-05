"""
This code tests the "digistamp" portion of the codebase.
"""

# Source imports.
from source.configs import (
    TEST_PATH_TO_DATA,
    TEST_PATH_TO_PRIVATE_KEY,
    TEST_PATH_TO_PUBLIC_KEY,
    TEST_PASSWORD
)
from source.digistamp import StampMachine, Verifier
from source.utils import remove_data_dir

# Local imports.
from utils import construct_test_data

###########
# TESTING #
###########

def test_stamp_machine_and_verifier():
    """ (1) Set up; (2) create a stamp object; (3) use that stamp to test the
    Verifier class; (4) clean. """
    good_data = "123"
    bad_data = "abc"
    # Set up.
    construct_test_data()
    # Create stamp.
    stamp_machine = \
        StampMachine(
            path_to_private_key=TEST_PATH_TO_PRIVATE_KEY,
            password=TEST_PASSWORD
        )
    stamp = stamp_machine.make_stamp(good_data)
    # Test verifier class.
    verifier = Verifier(path_to_public_key=TEST_PATH_TO_PUBLIC_KEY)
    assert verifier.verify(good_data, stamp)
    assert not verifier.verify(bad_data, stamp)
    # Clean.
    remove_data_dir(path_to_data=TEST_PATH_TO_DATA)
