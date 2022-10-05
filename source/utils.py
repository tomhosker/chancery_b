"""
This code defines some utility functions for the codebase as a whole.
"""

# Standard imports.
import hashlib
import shutil
from pathlib import Path

# Local imports.
from .configs import DEFAULT_LEDGER_FN, DEFAULT_PATH_OBJ_TO_DATA, ENCODING

# Local constants.
DEFAULT_PATH_TO_DATA = str(DEFAULT_PATH_OBJ_TO_DATA)
PATH_TO_EMPTY_LEDGER = str(Path(__file__).parent/"db"/"empty_ledger.db")

#############
# FUNCTIONS #
#############

def dict_factory(cursor, row):
    """ A function which allows queries to return dictionaries, rather than
    default tuples. """
    result = {}
    for idx, col in enumerate(cursor.description):
        result[col[0]] = row[idx]
    return result

def get_hash_of_ordinance(ordinance):
    """ Get a hash of the attributes of a given ordinance object. """
    hash_maker = hashlib.sha256()
    hash_maker.update(bytes(ordinance.ordinal))
    hash_maker.update(bytes(ordinance.ordinance_type, ENCODING))
    hash_maker.update(bytes(ordinance.latex, ENCODING))
    hash_maker.update(bytes(ordinance.year))
    hash_maker.update(bytes(ordinance.month_num))
    hash_maker.update(bytes(ordinance.day))
    if ordinance.annexe:
        hash_maker.update(ordinance.annexe)
    hash_maker.update(bytes(ordinance.prev, ENCODING))
    result = hash_maker.hexdigest()
    return result

def trim_brackets(raw):
    """ Trim the brackets from a string. """
    if not raw:
        return None
    result = raw[1:-1]
    return result

def trim_and_cast_hex(raw):
    """ Trim a string of hexadecimal, and then convert it back to bytes. """
    if not raw:
        return None
    trimmed = trim_brackets(raw)
    result = bytes.fromhex(trimmed)
    return result

def raw_to_usable(raw):
    """ Convert the raw bytes into a more usable form. """
    if not raw:
        return None
    raw_is_string = isinstance(raw, str)
    result = str(raw)
    result = result[1:-1]
    if not raw_is_string:
        result = bytes.fromhex(result)
    return result

def create_data_dir_as_necessary(
        path_to_data=DEFAULT_PATH_TO_DATA,
        ledger_fn=DEFAULT_LEDGER_FN
    ):
    """ Create the data directory, if it doesn't exist. """
    path_obj_to_data = Path(path_to_data)
    path_to_ledger = str(path_obj_to_data/ledger_fn)
    if not path_obj_to_data.exists():
        path_obj_to_data.mkdir(parents=True)
        shutil.copyfile(PATH_TO_EMPTY_LEDGER, path_to_ledger)

def remove_data_dir(path_to_data=DEFAULT_PATH_TO_DATA):
    """ Delete the data directory, if it exists. """
    shutil.rmtree(path_to_data, ignore_errors=True)
