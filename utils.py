# Utility functions (not methods) used in multiple scripts
import logging

logger = logging.getLogger(__name__)

# ======================================================================================= CHJ =====
def extract_tile_prefix(filename):
    """
    Normalize filename to tile prefix:
    - remove .nc extension
    - remove .tile#
    - remove trailing .tile
    """
    import os
    import re

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


# ======================================================================================= CHJ =====
def to_dict(obj):
    """
    Convert Config or dict-like object to plain dict.
    """
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "_config"):
        return obj._config
    return {}


# ======================================================================================= CHJ =====
def to_plain_dict(obj):
    if isinstance(obj, dict):
        return {k: to_plain_dict(v) for k, v in obj.items()}
    if hasattr(obj, "_config"):
        return to_plain_dict(obj._config)
    return obj


# ======================================================================================= CHJ =====
def to_plain(obj):
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    if hasattr(obj, "_config"):
        return to_plain(obj._config)
    return obj

