"""
This code defines some configurations used across the codebase.
"""

# Local imports.
from pathlib import Path

# Local constants.
PATH_OBJ_TO_DATA = Path.home()/"chancery_b_data"

###########
# CONFIGS #
###########

# Paths.
PATH_TO_PRIVATE_KEY = str(PATH_OBJ_TO_DATA/"stamp_private_key.pem")
PATH_TO_PUBLIC_KEY = str(PATH_OBJ_TO_DATA/"stamp_public_key.pem")
PATH_TO_LEDGER = str(PATH_OBJ_TO_DATA/"ledger.db")
PATH_TO_EXTRACTS = str(PATH_OBJ_TO_DATA/"extracts")

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

# Other.
ENCODING = "utf-8"
COMPRESSION_FORMAT = "zip"
COMPRESSION_EXT = ".zip"
ANNEXE = "annexe"
ARCHIVE_FN = ANNEXE+COMPRESSION_EXT
