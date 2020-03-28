### This code defines a class, which uploads a record to the ledger.

# Imports.
import datetime, hashlib, os, sqlite3

# Local imports.
from digistamp.digistamp import Stamp_Machine
import ordinance_inputs

# Constants.
encoding = "utf-8"

##############
# MAIN CLASS #
##############

# The class in question.
class Uploader:
    def __init__(self):
        self.connection = None
        self.c = None
        self.block = Block_of_Ledger()

    # Ronseal.
    def make_connection(self):
        self.connection = sqlite3.connect("ledger.db")
        self.connection.row_factory = dict_factory
        self.c = self.connection.cursor()

    # Ronseal.
    def close_connection(self):
        self.connection.close()

    # Add the ordinal and the previous block's hash to the block.
    def add_ordinal_and_prev(self):
        self.make_connection()
        query = "SELECT * FROM Block ORDER BY ordinal DESC;"
        self.c.execute(query)
        result = self.c.fetchone()
        self.close_connection()
        if result is None:
            self.block.set_ordinal(1)
            self.block.set_prev("genesis")
        else:
            self.block.set_ordinal(result["ordinal"]+1)
            self.block.set_prev(result["hash"])

    # Add the hash to the present block.
    def add_hash(self):
        m = hashlib.sha256()
        m.update(bytes(self.block.ordinal))
        m.update(bytes(self.block.ordinance_type, encoding))
        m.update(bytes(self.block.latex, encoding))
        m.update(bytes(self.block.year))
        m.update(bytes(self.block.month))
        m.update(bytes(self.block.day))
        if self.block.annexe:
            m.update(self.block.annexe)
        m.update(bytes(self.block.prev, encoding))
        self.block.set_the_hash(m.hexdigest())

    # Add a new block to the legder.
    def add_new_block(self):
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
        self.c.execute(query, new_block_tuple)
        self.connection.commit()
        self.close_connection()

    # Construct a new block and add it to the chain.
    def upload(self):
        self.add_ordinal_and_prev()
        self.add_hash()
        self.add_new_block()

################################
# HELPER CLASSES AND FUNCTIONS #
################################

# A class to hold the properties of a block of the ledger.
class Block_of_Ledger:
    def __init__(self):
        dt = datetime.datetime.now()
        self.ordinal = None
        self.ordinance_type = ordinance_inputs.ordinance_type
        self.latex = ordinance_inputs.latex
        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.stamp = Stamp_Machine().make_stamp()
        self.annexe = annexe_to_bytes()
        self.prev = None
        self.the_hash = None

    # Assign a value to the "ordinal" field of this object.
    def set_ordinal(self, ordinal):
        self.ordinal = ordinal

    # Assign a value to the "prev" field of this object.
    def set_prev(self, prev):
        self.prev = prev

    # Assign a value to the "the_hash" field of this object.
    def set_the_hash(self, the_hash):
        self.the_hash = the_hash

# A function which allows queries to return dictionaries, rather than the
# default tuples.
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Convert the annexe folder to a zip, load the bytes thereof into memory,
# and then delete the zip.
def annexe_to_bytes():
    if len(os.listdir("annexe/")) == 0:
        return None
    os.system("zip -r annexe.zip annexe/")
    f = open("annexe.zip", "rb")
    result = f.read()
    f.close()
    os.system("rm annexe.zip")
    return result

###################
# RUN AND WRAP UP #
###################

def run():
    Uploader().upload()

if __name__ == "__main__":
    run()
