"""
This code defines some utility functions for the codebase as a whole.
"""

# Standard imports.
import hashlib

# Local imports.
from .configs import ENCODING

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

def raw_to_usable(raw):
    """ Convert the raw bytes into a more usable form. """
    if not raw:
        return None
    my_buffer = str(raw)
    my_buffer = my_buffer[1:-1]
    result = bytes.fromhex(my_buffer)
    return result
