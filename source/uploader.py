"""
This code defines a class which uploads an ordinance record to the ledger.
"""

# Standard imports.
import os
import sqlite3
from dataclasses import dataclass

# Local imports.
from .configs import PATH_TO_LEDGER, ORDINAL_COLUMN, HASH_COLUMN, GENESIS_KEY
from .digistamp import StampMachine
from .ordinance import Ordinance
from .utils import dict_factory, get_hash_of_ordinance

##############
# MAIN CLASS #
##############

class Uploader:
    """ The class question. """
    def __init__(self, ordinance):
        self.ordinance = ordinance
        self.connection = None
        self.cursor = None

    def make_connection(self):
        """ Ronseal. """
        self.connection = sqlite3.connect(PATH_TO_LEDGER)
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
        if result:
            self.ordinance.ordinal = result[ORDINAL_COLUMN]+1
            self.ordinance.prev = result[HASH_COLUMN]
        else:
            self.ordinance.ordinal = 1
            self.ordinance.prev = GENESIS_KEY

    def add_hash(self):
        """ Add the hash to the present block. """
        self.ordinance.hash = get_hash_of_ordinance(self.ordinance)
        self.ordinance.update_stamp()

    def add_new_block(self):
        """ Add a new block to the legder. """
        attributes_tuple = (
            "ordinal",
            "ordinance_type",
            "latex",
            "year",
            "month_num",
            "day",
            "stamp",
            "annexe",
            "prev",
            "hash"
        )
        new_block_list = []
        substitutes_list = []
        for attribute in attributes_tuple:
            new_block_list.append(getattr(self.ordinance, attribute))
            substitutes_list.append("?")
        query = (
            "INSERT INTO Block ("+", ".join(attributes_tuple)+") "+
            "VALUES ("+", ".join(substitutes_list)+");"
        )
        self.make_connection()
        self.cursor.execute(query, new_block_list)
        self.connection.commit()
        self.close_connection()

    def upload(self):
        """ Construct a new block and add it to the chain. """
        self.add_ordinal_and_prev()
        self.add_hash()
        self.add_new_block()
