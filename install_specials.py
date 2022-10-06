"""
This code installs any required software that cannot be installed
straightforwardly using the Setuptools utilities.
"""

# Non-standard imports.
from hosker_utils import install_apt_packages

# Local constants.
PACKAGES_TO_INSTALL = ("sqlitebrowser", "texlive-full")

###################
# RUN AND WRAP UP #
###################

def run():
    """ Run this file. """
    install_apt_packages(PACKAGES_TO_INSTALL)

if __name__ == "__main__":
    run()
