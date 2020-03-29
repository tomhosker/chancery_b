""" This code is a quick script which renews the public and private keys
used in making and verifying digital stamps. """

# Standard mports.
import os

# Local imports.
from digistamp import generate_keys

#############
# FUNCTIONS #
#############

def delete_keys():
    """ Delete the present public and private keys, if they exist. """
    print("Are you sure you wish to delete the current public and private "+
          "key? Changing keys may cause unforeseen problems.")
    print("Type \"y\" to continue.")
    response = input()
    if response == "y":
        os.system("rm -f stamp_private_key.pem")
        os.system("rm -f stamp_public_key.pem")
        return True
    return False

##############
# RUN SCRIPT #
##############

def run():
    delete_keys()
    generate_keys()
    print("New keys generated!")

if __name__ == "__main__":
    run()
