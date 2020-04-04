"""
This code defines a class which takes a given record in the ledger and
converts it into a directory.
"""

# Standard imports.
import os
import sqlite3
import sys

# Non-standard imports.
from pdfrw import PdfReader, PdfWriter

# Local imports.
from digistamp.digistamp import Verifier
from uploader import dict_factory

# Local constants.
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
               "Sep", "Oct", "Nov", "Dec"]
VERIFICATION_INSTRUCTIONS = ("To verify this Ordinance: (1) Verify that "+
                             "the hash matches the data. It should be the "+
                             "hex digest of the SHA256 hash of the data "+
                             "points. (2) Verify that the stamp matches "+
                             "the hash, using the public key, standard "+
                             "padding and, again, SHA256. (To make your "+
                             "life easier, you could just use the "+
                             "verification software provided by this "+
                             "office.)")

##############
# MAIN CLASS #
##############

class Extractor:
    """ The class in question. """
    def __init__(self, ordinal):
        self.ordinal = ordinal
        self.block = self.fetch_block()
        self.main_tex = self.make_main_tex()

    def fetch_block(self):
        """ Fetch the block matching this object's ordinal from the
        ledger. """
        connection = sqlite3.connect("ledger.db")
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        query = "SELECT * FROM Block WHERE ordinal = ?;"
        cursor.execute(query, (self.ordinal,))
        result = cursor.fetchone()
        connection.close()
        if result is None:
            raise Exception("No block with ordinal "+str(self.ordinal)+
                            " in the ledger.")
        return result

    def get_base(self):
        """ Get the base for main.tex, given the type of the Ordinance. """
        if self.block["ordinanceType"] == "Declaration":
            path_to_base = "latexery/base_declaration.tex"
        elif self.block["ordinanceType"] == "Order":
            path_to_base = "latexery/base_order.tex"
        else:
            raise Exception("Invalid ordinanceType: "+
                            self.block["ordinanceType"])
        with open(path_to_base, "r") as base_file:
            result = base_file.read()
        return result

    def make_main_tex(self):
        """ Make the code for main.tex, which will then be used build our
        PDF. """
        day_str = str(self.block["day"])
        if len(day_str) == 1:
            day_str = "0"+day_str
        packed_ordinal = str(self.ordinal)
        while len(packed_ordinal) < 3:
            packed_ordinal = "0"+packed_ordinal
        month_str = MONTH_NAMES[self.block["month"]-1]
        result = self.get_base()
        result = result.replace("#BODY", self.block["latex"])
        result = result.replace("#DAY_STR", day_str)
        result = result.replace("#MONTH_STR", month_str)
        result = result.replace("#YEAR", str(self.block["year"]))
        result = result.replace("#PACKED_ORDINAL", packed_ordinal)
        return result

    def authenticate(self):
        """ Check that the block isn't a forgery. """
        self.compare_hashes()
        self.verify_stamp()

    def compare_hashes(self):
        """ Compare the "prev" field of this block with the hash of the
        previous. """
        if self.ordinal == 1:
            if self.block["prev"] != "genesis":
                raise Exception("Block with ordinal=1 should be the "+
                                "genesis block.")
            return
        prev_ordinal = self.ordinal-1
        connection = sqlite3.connect("ledger.db")
        cursor = connection.cursor()
        query = "SELECT hash FROM Block WHERE ordinal = ?;"
        cursor.execute(query, (prev_ordinal,))
        extract = cursor.fetchone()
        connection.close()
        prev_hash = extract["0"]
        if prev_hash != self.block["prev"]:
            raise Exception("Block with ordinal="+str(self.ordinal)+" is "+
                            "not authentic: \"prev\" does not match "+
                            "previous \"hash\".")

    def verify_stamp(self):
        """ Check that this block's stamp is in order. """
        verifier = Verifier(self.block["stamp"], self.block["hash"])
        if not verifier.verify():
            raise Exception("Block with ordinal="+str(self.ordinal)+" is "+
                            "not authentic: \"prev\" does not match "+
                            "previous \"hash\".")

    def write_main_tex(self):
        """ Ronseal. """
        with open("latexery/main.tex", "w") as main_tex:
            main_tex.write(self.main_tex)

    def compile_main_tex(self):
        """ Compile the PDF. """
        script = ("cd latexery/\n"+
                  "pdflatex main.tex")
        os.system(script)

    def add_metadata(self):
        """ Add the verification metadata to the PDF. """
        os.system("mv latexery/main.pdf latexery/main_old.pdf")
        trailer = PdfReader("latexery/main_old.pdf")
        trailer.Info.instructions = VERIFICATION_INSTRUCTIONS
        trailer.Info.data_ordinal = self.block["ordinal"]
        trailer.Info.data_ordinanceType = self.block["ordinanceType"]
        trailer.Info.data_latex = self.block["latex"]
        trailer.Info.data_year = self.block["year"]
        trailer.Info.data_month = self.block["month"]
        trailer.Info.data_day = self.block["day"]
        decoded_annexe = self.block["annexe"].hex()
        trailer.Info.data_annexe = decoded_annexe
        trailer.Info.data_prev = self.block["prev"]
        trailer.Info.hash = self.block["hash"]
        trailer.Info.stamp = self.block["stamp"]
        PdfWriter("latexery/main.pdf", trailer=trailer).write()

    def create_and_copy(self):
        """ Create the directory, and copy the PDF into it. """
        if os.path.isdir("extracts/"+str(self.ordinal)+"/"):
            os.system("rm -r extracts/"+str(self.ordinal)+"/")
        os.system("mkdir extracts/"+str(self.ordinal)+"/")
        os.system("cp latexery/main.pdf extracts/"+str(self.ordinal)+"/")

    def write_annexe_zip(self):
        """ Write annexe to a file in the directory. """
        if self.block["annexe"] is None:
            return
        with open("extracts/"+str(self.ordinal)+"/annexe.zip", "wb") \
            as annexe_zip:
            annexe_zip.write(self.block["annexe"])

    def extract(self):
        """ Do the thing. """
        self.authenticate()
        self.write_main_tex()
        self.compile_main_tex()
        self.add_metadata()
        self.create_and_copy()
        self.write_annexe_zip()

    def zip_and_delete(self):
        """ Ronseal. """
        script = ("cd extracts/\n"+
                  "zip -r ordinance_"+str(self.ordinal)+".zip "+
                  str(self.ordinal)+"/\n"+
                  "rm -r "+str(self.ordinal)+"/")
        if os.path.exists("extracts/ordinance_"+str(self.ordinal)+".zip"):
            os.system("rm extracts/ordinance_"+str(self.ordinal)+".zip")
        os.system(script)

###########
# TESTING #
###########

def demo():
    """ Run a demonstration. """
    extractor = Extractor(1)
    extractor.extract()

###################
# RUN AND WRAP UP #
###################

def run():
    if len(sys.argv) == 2:
        extractor = Extractor(int(sys.argv[1]))
        extractor.extract()
    else:
        print("Please run me with exactly one argument, the number of the "+
              "Ordinance you wish to extract.")

if __name__ == "__main__":
    run()
