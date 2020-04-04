"""
This code defines a class, which uploads a record to the ledger.
"""

# Standard imports.
import datetime
import hashlib
import os
import sqlite3

# Local imports.
import ordinance_inputs
from digistamp.digistamp import StampMachine

# Local constants.
ENCODING = "utf-8"

##############
# MAIN CLASS #
##############

class Uploader:
    """ The class question. """
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.block = BlockOfLedger()

    def make_connection(self):
        """ Ronseal. """
        self.connection = sqlite3.connect("ledger.db")
        self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()

    def close_connection(self):
        """ Ronseal. """
        self.connection.close()

    def add_ordinal_and_prev(self):
        """ Add the ordinal and the previous block's hash to the block. """
        self.make_connection()
        query = "SELECT * FROM Block ORDER BY ordinal DESC;"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        self.close_connection()
        if result is None:
            self.block.set_ordinal(1)
            self.block.set_prev("genesis")
        else:
            self.block.set_ordinal(result["ordinal"]+1)
            self.block.set_prev(result["hash"])

    def add_hash(self):
        """ Add the hash to the present block. """
        hash_maker = hashlib.sha256()
        hash_maker.update(bytes(self.block.ordinal))
        hash_maker.update(bytes(self.block.ordinance_type, ENCODING))
        hash_maker.update(bytes(self.block.latex, ENCODING))
        hash_maker.update(bytes(self.block.year))
        hash_maker.update(bytes(self.block.month))
        hash_maker.update(bytes(self.block.day))
        if self.block.annexe:
            hash_maker.update(self.block.annexe)
        hash_maker.update(bytes(self.block.prev, ENCODING))
        self.block.set_the_hash(hash_maker.hexdigest())

    def add_new_block(self):
        """ Add a new block to the legder. """
        new_block_tuple = (self.block.ordinal, self.block.ordinance_type,
                           self.block.latex, self.block.year,
                           self.block.month, self.block.day,
                           self.block.stamp, self.block.annexe,
                           self.block.prev, self.block.the_hash)
        query = ("INSERT INTO Block (ordinal, ordinanceType, latex, year, "+
                 "                   month, day, stamp, annexe, prev, "+
                 "                   hash) "+
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);")
        self.make_connection()
        self.cursor.execute(query, new_block_tuple)
        self.connection.commit()
        self.close_connection()

    def upload(self):
        """ Construct a new block and add it to the chain. """
        self.add_ordinal_and_prev()
        self.add_hash()
        self.add_new_block()

################################
# HELPER CLASSES AND FUNCTIONS #
################################

class BlockOfLedger:
    """ A class to hold the properties of a block of the ledger. """
    def __init__(self):
        date_and_time = datetime.datetime.now()
        self.ordinal = None
        self.ordinance_type = ordinance_inputs.ordinance_type
        self.latex = ordinance_inputs.latex
        self.year = date_and_time.year
        self.month = date_and_time.month
        self.day = date_and_time.day
        self.annexe = annexe_to_bytes()
        self.prev = None
        self.the_hash = None
        self.stamp = None

    def set_ordinal(self, ordinal):
        """ Assign a value to the "ordinal" field of this object. """
        self.ordinal = ordinal

    def set_prev(self, prev):
        """ Assign a value to the "prev" field of this object. """
        self.prev = prev

    def set_the_hash(self, the_hash):
        """ Assign a value to the "the_hash" field of this object. """
        self.the_hash = the_hash
        self.stamp = StampMachine(self.the_hash).make_stamp()

def dict_factory(cursor, row):
    """ A function which allows queries to return dictionaries, rather than
    default tuples. """
    result = {}
    for idx, col in enumerate(cursor.description):
        result[col[0]] = row[idx]
    return result

def annexe_to_bytes():
    """ Convert the annexe folder to a zip, load the bytes thereof into
    memory, and then delete the zip. """
    if len(os.listdir("annexe/")) == 0:
        return None
    os.system("zip -r annexe.zip annexe/")
    with open("annexe.zip", "rb") as annexe_zip:
        result = annexe_zip.read()
    os.system("rm annexe.zip")
    return result

###################
# RUN AND WRAP UP #
###################

def run():
    Uploader().upload()

if __name__ == "__main__":
    run()
