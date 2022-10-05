"""
This code defines a class which takes a reference to given record in the ledger
and converts it into a directory.
"""

# Standard imports.
import glob
import os
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

# Non-standard imports.
from pdfrw import PdfReader, PdfWriter

# Local imports.
from .configs import (
    DEFAULT_PATH_TO_LEDGER,
    DEFAULT_PATH_TO_EXTRACTS,
    DEFAULT_PATH_TO_PUBLIC_KEY,
    ORDINAL_COLUMN,
    ORDINANCE_TYPE_COLUMN,
    LATEX_COLUMN,
    DAY_COLUMN,
    MONTH_COLUMN,
    YEAR_COLUMN,
    HASH_COLUMN,
    PREV_COLUMN,
    ANNEXE_COLUMN,
    STAMP_COLUMN,
    DECLARATION_KEY,
    ORDER_KEY,
    GENESIS_KEY,
    ANNEXE,
    COMPRESSION_FORMAT,
    ARCHIVE_FN
)
from .digistamp import Verifier
from .utils import dict_factory

# Local constants.
MONTH_NAMES = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
)
VERIFICATION_INSTRUCTIONS = (
    "To verify this Ordinance: (1) Verify that the hash matches the data. "+
    "It should be the hex digest of the SHA256 hash of the data points. (2) "+
    "Verify that the stamp matches the hash, using the public key, standard "+
    "padding and, again, SHA256. (To make your life easier, you could just "+
    "use the verification software provided by this office.)"
)
MIN_PACKED_ORDINAL_LENGTH = 3
# Paths.
PATH_OBJ_TO_TEX = Path(__file__).parent/"tex"
PATH_TO_DECLARATION_BASE = str(PATH_OBJ_TO_TEX/"base_declaration.tex")
PATH_TO_ORDER_BASE = str(PATH_OBJ_TO_TEX/"base_order.tex")
# Markers.
BODY_MARKER = "#BODY"
DAY_STR_MARKER = "#DAY_STR"
MONTH_STR_MARKER = "#MONTH_STR"
YEAR_MARKER = "#YEAR"
PACKED_ORDINAL_MARKER = "#PACKED_ORDINAL"
PATH_TO_IMAGES_MARKER = "#PATH_TO_IMAGES"

##############
# MAIN CLASS #
##############

@dataclass
class Extractor:
    """ The class in question. """
    # Class attributes.
    LATEX_COMMAND: ClassVar[str] = "pdflatex"
    WORKING_STEM: ClassVar[str] = "main"
    OLD_SUFFIX: ClassVar[str] = "_old"

    # Instance attributes.
    ordinal: int
    path_to_extracts: str = DEFAULT_PATH_TO_EXTRACTS
    path_to_ledger: str = DEFAULT_PATH_TO_LEDGER
    path_to_public_key: str = DEFAULT_PATH_TO_PUBLIC_KEY
    path_obj_to_extract: Path = None
    block: tuple = None
    main_tex: str = None
    clean_flag: bool = True
    purge_existing: bool = False

    def __post_init__(self):
        self.path_obj_to_extract = \
            Path(self.path_to_extracts)/str(self.ordinal)
        self.block = self.fetch_block(self.ordinal)
        self.main_tex = self.make_main_tex()
        if self.purge_existing:
            shutil.rmtree(self.path_to_extracts, ignore_errors=True)

    def fetch_block(self, local_ordinal):
        """ Fetch the block matching this object's ordinal from the ledger. """
        connection = sqlite3.connect(self.path_to_ledger)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        query = "SELECT * FROM Block WHERE ordinal = ?;"
        cursor.execute(query, (local_ordinal,))
        result = cursor.fetchone()
        connection.close()
        if not result:
            raise ExtractorError("No block with ordinal: "+str(self.ordinal))
        return result

    def get_base(self):
        """ Get the base for main.tex, given the type of the ordinance. """
        col_id = ORDINANCE_TYPE_COLUMN
        if self.block[col_id] == DECLARATION_KEY:
            path_to_base = PATH_TO_DECLARATION_BASE
        elif self.block[col_id] == ORDER_KEY:
            path_to_base = PATH_TO_ORDER_BASE
        else:
            raise ExtractorError("Invalid "+col_id+": "+self.block[col_id])
        with open(path_to_base, "r") as base_file:
            result = base_file.read()
        return result

    def make_main_tex(self):
        """ Make the code for main.tex, which will then be used build our
        PDF. """
        day_str = str(self.block[DAY_COLUMN])
        if len(day_str) == 1:
            day_str = "0"+day_str
        packed_ordinal = str(self.ordinal)
        while len(packed_ordinal) < MIN_PACKED_ORDINAL_LENGTH:
            packed_ordinal = "0"+packed_ordinal
        month_str = MONTH_NAMES[self.block[MONTH_COLUMN]-1]
        result = self.get_base()
        result = result.replace(BODY_MARKER, self.block[LATEX_COLUMN])
        result = result.replace(DAY_STR_MARKER, day_str)
        result = result.replace(MONTH_STR_MARKER, month_str)
        result = result.replace(YEAR_MARKER, str(self.block[YEAR_COLUMN]))
        result = result.replace(PACKED_ORDINAL_MARKER, packed_ordinal)
        result = \
            result.replace(
                PATH_TO_IMAGES_MARKER, str(Path(__file__).parent/"images")
            )
        return result

    def authenticate(self):
        """ Check that the block isn't a forgery. """
        self.compare_hashes()
        self.verify_stamp()

    def compare_hashes(self):
        """ Compare the "prev" field of this block with the hash of the
        previous. """
        if self.ordinal == 1:
            if self.block[PREV_COLUMN] != GENESIS_KEY:
                raise ExtractorError(
                    "Block with ordinal 1 should be the genesis block."
                )
            return
        prev_block = self.fetch_block(self.ordinal-1)
        if prev_block[HASH_COLUMN] != self.block[PREV_COLUMN]:
            raise ExtractorError(
                "Block with ordinal "+str(self.ordinal)+" is not authentic: "+
                "\"prev\" does not match previous hash."
            )

    def verify_stamp(self):
        """ Check that this block's stamp is in order. """
        verifier = Verifier(path_to_public_key=self.path_to_public_key)

        print("Extractor - hash:")
        print(self.block[HASH_COLUMN])
        print("Extractor - stamp:")
        print(self.block[STAMP_COLUMN])

        verified = \
            verifier.verify(self.block[HASH_COLUMN], self.block[STAMP_COLUMN])
        if not verified:
            raise ExtractorError(
                "Block with ordinal "+str(self.ordinal)+" is not authentic: "+
                "its stamp cannot be verified against its hash."
            )

    def write_main_tex(self):
        """ Ronseal. """
        with open(self.WORKING_STEM+".tex", "w") as main_tex:
            main_tex.write(self.main_tex)

    def compile_main_tex(self):
        """ Compile the PDF. """
        subprocess.run(
            [self.LATEX_COMMAND, self.WORKING_STEM+".tex"], check=True
        )

    def get_decoded_annexe(self):
        """ Get the annexe field, if it exists, and decode it. """
        result = None
        if self.block[ANNEXE_COLUMN]:
            result = self.block[ANNEXE_COLUMN].hex()
        return result

    def add_metadata(self):
        """ Add the verification metadata to the PDF. """
        path_to_old = self.WORKING_STEM+self.OLD_SUFFIX+".pdf"
        os.rename(self.WORKING_STEM+".pdf", path_to_old)
        trailer = PdfReader(path_to_old)
        trailer.Info.instructions = VERIFICATION_INSTRUCTIONS
        trailer.Info.data_ordinal = self.block[ORDINAL_COLUMN]
        trailer.Info.data_ordinance_type = self.block[ORDINANCE_TYPE_COLUMN]
        trailer.Info.data_latex = self.block[LATEX_COLUMN]
        trailer.Info.data_year = self.block[YEAR_COLUMN]
        trailer.Info.data_month = self.block[MONTH_COLUMN]
        trailer.Info.data_day = self.block[DAY_COLUMN]
        trailer.Info.data_annexe = self.get_decoded_annexe()
        trailer.Info.data_prev = self.block[PREV_COLUMN]
        trailer.Info.hash = self.block[HASH_COLUMN]
        trailer.Info.stamp = self.block[STAMP_COLUMN]
        PdfWriter(self.WORKING_STEM+".pdf", trailer=trailer).write()

    def create_and_copy(self):
        """ Create the extract directory, and copy the PDF into it. """
        source_fn = self.WORKING_STEM+".pdf"
        path_to_dest = str(self.path_obj_to_extract/source_fn)
        self.path_obj_to_extract.mkdir(parents=True, exist_ok=True)
        os.rename(source_fn, path_to_dest)

    def write_and_unpack_annexe(self):
        """ Write annexe to a file in the directory. """
        archive_bytes = self.block[ANNEXE_COLUMN]
        if archive_bytes:
            with open(ARCHIVE_FN, "wb") as archive_file:
                archive_file.write(archive_bytes)
            path_to_annexe = str(self.path_obj_to_extract/ANNEXE)
            shutil.unpack_archive(
                ARCHIVE_FN, path_to_annexe, COMPRESSION_FORMAT
            )

    def clean(self):
        """ Clean up any temporary generated files. """
        files_to_delete = (
            [ARCHIVE_FN]+
            glob.glob(self.WORKING_STEM+".*")+
            glob.glob(self.WORKING_STEM+self.OLD_SUFFIX+".*")
        )
        for filename in files_to_delete:
            try:
                os.remove(filename)
            except OSError:
                pass

    def extract(self):
        """ Do the thing. """
        self.authenticate()
        self.write_main_tex()
        self.compile_main_tex()
        self.add_metadata()
        self.create_and_copy()
        self.write_and_unpack_annexe()
        if self.clean_flag:
            self.clean()
        result = str(self.path_obj_to_extract.resolve())
        return result

################
# HELPER CLASS #
################

class ExtractorError(Exception):
    """ A custom exception. """
