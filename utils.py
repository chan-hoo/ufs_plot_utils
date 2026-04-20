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
    logger.debug(f'''File prefix input: {name}''')

    # Remove extension if present
    base, ext = os.path.splitext(name)

    if ext == ".nc":
        logger.debug(f'''Remove extension: {base}''')
    else:
        base = name  # keep original if no extension

    # Remove ".tile<number>" if present
    base = re.sub(r'\.tile\d+$', '', base)

    # Remove trailing ".tile"
    base = re.sub(r'\.tile$', '', base)

    logger.debug(f'''File prefix final: {base}''')

    return base

