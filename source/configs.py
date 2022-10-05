"""
This code defines some configurations used across the codebase.
"""

# Local imports.
from pathlib import Path

###########
# CONFIGS #
###########

# General.
ENCODING = "utf-8"
COMPRESSION_FORMAT = "zip"
COMPRESSION_EXT = ".zip"
ANNEXE = "annexe"
# General TEST configs.
TEST_PASSWORD = "guest"

# Path objects.
DEFAULT_PATH_OBJ_TO_DATA = Path.home()/"chancery_b_data"
# Test path objects.
TEST_PATH_OBJ_TO_DATA = Path("test_data")

# Filenames.
ARCHIVE_FN = ANNEXE+COMPRESSION_EXT
DEFAULT_LEDGER_FN = "ledger.db"
DEFAULT_PRIVATE_KEY_FN = "stamp_private_key.pem"
DEFAULT_PUBLIC_KEY_FN = "stamp_public_key.pem"
# Test filenames.
TEST_LEDGER_FN = "test_"+DEFAULT_LEDGER_FN
TEST_PRIVATE_KEY_FN = "test_"+DEFAULT_PRIVATE_KEY_FN
TEST_PUBLIC_KEY_FN = "test_"+DEFAULT_PUBLIC_KEY_FN

# Paths.
DEFAULT_PATH_TO_PRIVATE_KEY = \
    str(DEFAULT_PATH_OBJ_TO_DATA/DEFAULT_PRIVATE_KEY_FN)
DEFAULT_PATH_TO_PUBLIC_KEY = \
    str(DEFAULT_PATH_OBJ_TO_DATA/DEFAULT_PUBLIC_KEY_FN)
DEFAULT_PATH_TO_LEDGER = str(DEFAULT_PATH_OBJ_TO_DATA/DEFAULT_LEDGER_FN)
DEFAULT_PATH_TO_EXTRACTS = str(DEFAULT_PATH_OBJ_TO_DATA/"extracts")
# Test paths.
TEST_PATH_TO_DATA = str(TEST_PATH_OBJ_TO_DATA)
TEST_PATH_TO_LEDGER = str(TEST_PATH_OBJ_TO_DATA/TEST_LEDGER_FN)
TEST_PATH_TO_PRIVATE_KEY = str(TEST_PATH_OBJ_TO_DATA/TEST_PRIVATE_KEY_FN)
TEST_PATH_TO_PUBLIC_KEY = str(TEST_PATH_OBJ_TO_DATA/TEST_PUBLIC_KEY_FN)
TEST_PATH_TO_EXTRACTS = str(TEST_PATH_OBJ_TO_DATA/"extracts")

# Ledger columns and keys.
ORDINAL_COLUMN = "ordinal"
ORDINANCE_TYPE_COLUMN = "ordinance_type"
LATEX_COLUMN = "latex"
DAY_COLUMN = "day"
MONTH_COLUMN = "month_num"
YEAR_COLUMN = "year"
HASH_COLUMN = "hash"
PREV_COLUMN = "prev"
ANNEXE_COLUMN = "annexe"
STAMP_COLUMN = "stamp"
DECLARATION_KEY = "declaration"
ORDER_KEY = "order"
GENESIS_KEY = "genesis"
