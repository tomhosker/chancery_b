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
