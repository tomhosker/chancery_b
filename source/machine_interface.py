"""
This code defines a number of functions which together provide the machine
interface for rest of the codebase.
"""

# Standard imports.
import json
import shutil
from pathlib import Path

# Local imports.
from .configs import PATH_OBJ_TO_DATA, PATH_TO_LEDGER
from .extractor import Extractor
from .ordinance import Ordinance
from .uploader import Uploader

#############
# FUNCTIONS #
#############

def upload_ordinance_from_input_file(path_to_input_file):
    """ Ronseal. """
    with open(path_to_input_file, "r") as input_file:
        input_dict = json.loads(input_file.read())
    ordinance = Ordinance(**input_dict)
    uploader = Uploader(ordinance)
    uploader.upload()

def extract_ordinance_with_ordinal(ordinal):
    """ Ronseal. """
    extractor = Extractor(ordinal)
    result = extractor.extract()
    return result

def create_data_dir_as_necessary():
    """ Create the data directory, if it doesn't exist. """
    path_to_empty_ledger = str(Path(__file__).parent/"db"/"empty_ledger.db")
    if not PATH_OBJ_TO_DATA.exists():
        PATH_OBJ_TO_DATA.mkdir(parents=True)
        shutil.copyfile(path_to_empty_ledger, PATH_TO_LEDGER)
