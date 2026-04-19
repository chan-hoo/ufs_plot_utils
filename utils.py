# Utility functions (not methods) used in multiple scripts
import logging
import os
import re

logger = logging.getLogger(__name__)


# ======================================================================================= CHJ =====
def extract_tile_prefix(filename):
    """
    Normalize filename to tile prefix:
    - remove .nc extension
    - remove .tile#
    - remove trailing .tile
    """
    name = filename.strip()

    logger.debug(f'''File prefix: {name}''')
    # Remove extension
    if filename.endswith(".nc"):
        base = os.path.splitext(name)[0]
        logger.debug(f'''Remove extention: {base}''')
        ## Remove ".tile<number>" if present
        base = re.sub(r'\.tile\d+$', '', base)
    # Remove trailing ".tile" if present
    elif filename.endswith(".tile"):
        base = os.path.splitext(name)[0]
        logger.debug(f'''Remove .tile: {base}''')
    else:
        base = name

    logger.debug(f'''File prefix final: {base}''')

    return base

