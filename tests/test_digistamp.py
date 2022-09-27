"""
This code tests the "digistamp" portion of the codebase.
"""

# Standard imports.
import os

# Source imports.
from source.digistamp import StampMachine, Verifier, generate_keys

# Local constants.
TEST_PATH_TO_PRIVATE_KEY = "temp_private_key.pem"
TEST_PATH_TO_PUBLIC_KEY = "temp_public_key.pem"
TEST_PASSWORD = "guest"

###########
# TESTING #
###########

def test_stamp_machine_and_verifier():
    """ (1) Generate temporary private and public keys; (2) use those keys in
    conjuction with the StampMachine class to create a stamp; (3) use that
    stamp to test the Verifier class. """
    good_data = "123"
    bad_data = "abc"
    # Generate keys.
    generate_keys(
        path_to_private_key=TEST_PATH_TO_PRIVATE_KEY,
        path_to_public_key=TEST_PATH_TO_PUBLIC_KEY,
        password=TEST_PASSWORD
    )
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
    os.remove(TEST_PATH_TO_PRIVATE_KEY)
    os.remove(TEST_PATH_TO_PUBLIC_KEY)
