"""
This code defines a script which runs a minimal continuous integration routine.
"""

# Bespoke imports.
from hosker_utils.continuous_integration import run_continuous_integration

###################
# RUN AND WRAP UP #
###################

if __name__ == "__main__":
    run_continuous_integration()
