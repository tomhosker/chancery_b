#!/bin/sh

# This script installs the APT packages required by the codebase, or which
# can make using the codebase a bit easier.

# Constants.
PACKAGES = "sqlitebrowser texlive-full"

# Let's get cracking.
sudo apt install --yes $PACKAGES
