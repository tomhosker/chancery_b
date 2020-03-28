### This code defines a class which takes a given record in the ledger and
### converts it into a directory.

# Imports.
from uploader import dict_factory
import os, sqlite3, sys

# Local imports.
from digistamp.digistamp import Verifier

# Constants.
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
               "Sep", "Oct", "Nov", "Dec"]

##############
# MAIN CLASS #
##############

# The class in question.
class Extractor:
    def __init__(self, ordinal):
        self.ordinal = ordinal
        self.block = self.fetch_block()
        self.main_tex = self.make_main_tex()

    # Fetch the block matching this object's ordinal from the ledger.
    def fetch_block(self):
        connection = sqlite3.connect("ledger.db")
        connection.row_factory = dict_factory
        c = connection.cursor()
        query = "SELECT * FROM Block WHERE ordinal = ?;"
        c.execute(query, (self.ordinal,))
        result = c.fetchone()
        connection.close()
        if result is None:
            raise Exception("No block with ordinal "+str(self.ordinal)+
                            " in the ledger.")
        return result

    # Get the base for main.tex, given the type of the Ordinance.
    def get_base(self):
        if self.block["ordinanceType"] == "Decleration":
            path_to_base = "latexery/base_decleration.tex"
        elif self.block["ordinanceType"] == "Order":
            path_to_base = "latexery/base_order.tex"
        else:
            raise Exception("Invalid ordinanceType: "+
                            self.block["ordinanceType"])
        f = open(path_to_base, "r")
        result = f.read()
        f.close()
        return result

    # Make the code for main.tex, which will then be used build our PDF.
    def make_main_tex(self):
        day_str = str(self.block["day"])
        if len(day_str) == 0:
            day_str = "0"+day_str
        packed_ordinal = str(self.ordinal)
        while len(packed_ordinal) < 3:
            packed_ordinal = "0"+packed_ordinal
        month_str = month_names[self.block["month"]-1]
        result = self.get_base()
        result = result.replace("#BODY", self.block["latex"])
        result = result.replace("#DAY_STR", day_str)
        result = result.replace("#MONTH_STR", month_str)
        result = result.replace("#YEAR", str(self.block["year"]))
        result = result.replace("#PACKED_ORDINAL", packed_ordinal)
        result = result.replace("#DIGISTAMP", self.block["stamp"])
        return result

    # Check that the block isn't a forgery.
    def authenticate(self):
        self.compare_hashes()
        self.verify_stamp()

    # Compare the "prev" field of this block with the hash of the previous.
    def compare_hashes(self):
        if self.ordinal == 1:
            if self.block["prev"] != "genesis":
                raise Exception("Block with ordinal=1 should be the "+
                                "genesis block.")
            else:
                return
        prev_ordinal = self.ordinal-1
        connection = sqlite3.connect("ledger.db")
        c = connection.cursor()
        query = "SELECT hash FROM Block WHERE ordinal = ?;"
        c.execute(query, (prev_ordinal,))
        extract = c.fetchone()
        connection.close()
        prev_hash = extract["0"]
        if prev_hash != self.block["prev"]:
            raise Exception("Block with ordinal="+str(self.ordinal)+" is "+
                            "not authentic: \"prev\" does not match "+
                            "previous \"hash\".")

    # Check that this block's stamp is in order.
    def verify_stamp(self):
        v = Verifier(self.block["stamp"], self.block["hash"])
        if v.verify() == False:
            raise Exception("Block with ordinal="+str(self.ordinal)+" is "+
                            "not authentic: \"prev\" does not match "+
                            "previous \"hash\".")

    # Ronseal.
    def write_main_tex(self):
        f = open("latexery/main.tex", "w")
        f.write(self.main_tex)
        f.close()

    # Compile the PDF.
    def compile_main_tex(self):
        script = ("cd latexery/\n"+
                  "pdflatex main.tex")
        os.system(script)

    # Create the directory, and copy the PDF into it.
    def create_and_copy(self):
        script1 = ("cd extracts/\n"+
                   "mkdir "+str(self.ordinal)+"/")
        script2 = "cp latexery/main.pdf extracts/"+str(self.ordinal)+"/"
        if os.path.isdir("extracts/"+str(self.ordinal)+"/"):
            os.system("rm -r extracts/"+str(self.ordinal)+"/")
        os.system(script1)
        os.system(script2)

    # Write annexe to a file in the directory.
    def write_annexe_zip(self):
        if self.block["annexe"] is None:
            return
        f = open("extracts/"+str(self.ordinal)+"/annexe.zip", "wb")
        f.write(self.block["annexe"])
        f.close()

    # Do the thing.
    def extract(self):
        self.authenticate()
        self.write_main_tex()
        self.compile_main_tex()
        self.create_and_copy()
        self.write_annexe_zip()

    # Ronseal.
    def zip_and_delete(self):
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

# Run a demonstration.
def demo():
    e = Extractor(1)
    e.extract()
    #e.zip_and_delete()

###################
# RUN AND WRAP UP #
###################

def run():
    if len(sys.argv) == 2:
        e = Extractor(int(sys.argv[1]))
        e.extract()
    else:
        print("Please run me with exactly one argument, the number of the "+
              "Ordinance you wish to extract.")

if __name__ == "__main__":
    run()
