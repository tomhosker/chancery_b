"""
This code defines a class which models the properties of an ordinance.
"""

# Standard imports.
import shutil
from dataclasses import dataclass
from pathlib import Path

# Local imports.
from .configs import ANNEXE, ARCHIVE_FN, COMPRESSION_FORMAT, ENCODING
from .utils import trim_brackets, trim_and_cast_hex

##############
# MAIN CLASS #
##############

@dataclass
class Ordinance:
    """ The class in question. """
    # Object attributes.
    ordinal: int = None
    ordinance_type: str = None
    latex: str = None
    year: int = None
    month_num: int = None
    day: int = None
    annexe_path: str = None # A path to a folder of annexe data.
    annexe: bytes = None
    prev: str = None
    hash: str = None
    stamp: str = None
    clean_flag: bool = True

    def __post_init__(self):
        self.update_annexe()
        if self.clean_flag:
            self.clean()

    def load_from_trailer(self, trailer):
        """ Fill the attributes of this object using a trailer object. """
        try:
            self.ordinal = int(trailer.Info.data_ordinal)
            self.ordinance_type = trim_brackets(trailer.Info.data_ordinance_type)
            self.latex = trim_brackets(trailer.Info.data_latex)
            self.year = int(trailer.Info.data_year)
            self.month_num = int(trailer.Info.data_month)
            self.day = int(trailer.Info.data_day)
            self.prev = trim_brackets(trailer.Info.data_prev)
            self.annexe = trim_and_cast_hex(trailer.Info.data_annexe)
        except Exception as my_exception:
            message = "Error loading metadata: "+str(my_exception)
            raise OrdinanceError(message) from my_exception

    def update_stamp(self, stamp_machine):
        """ Update the stamp attribute, in order to reflect a change in the
        hash attribute. """
        self.stamp = stamp_machine.make_stamp(self.hash)

    def clean(self):
        """ Clean up any temporary generated files. """
        shutil.rmtree(ANNEXE, ignore_errors=True)

    def update_annexe(self):
        """ Update the annexe attribute, on the basis of what's in the
        annexe_path attribute. """
        if self.annexe or not self.annexe_path:
            return
        # Copy the folder.
        dest_folder_obj = Path(ANNEXE)
        if dest_folder_obj.exists():
            raise OrdinanceError(
                "Annexe folder already exists at path: "+str(dest_folder_obj)
            )
        shutil.copytree(self.annexe_path, ANNEXE)
        # Zip the folder.
        shutil.make_archive(ANNEXE, COMPRESSION_FORMAT, ANNEXE)
        # Read in the zip file as binary, and update the annexe attribute.
        with open(ARCHIVE_FN, "rb") as archive_file:
            self.annexe = archive_file.read()

################
# HELPER CLASS #
################

class OrdinanceError(Exception):
    """ A custom exception. """
