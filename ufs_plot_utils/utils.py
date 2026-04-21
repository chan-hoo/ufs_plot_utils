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


# ======================================================================================= CHJ =====
def normalize_tile_dims(da):
    dims = list(da.dims)

    # -------------------------
    # TILE
    # -------------------------
    tile_dim = next((d for d in dims if "tile" in d.lower()), None)

    # -------------------------
    # STRICT axis mapping (IMPORTANT)
    # -------------------------
    y_map = [
        "yaxis_1",
        "grid_yt",
        "lat",
        "latitude",
        "y"
    ]

    x_map = [
        "xaxis_1",
        "grid_xt",
        "lon",
        "longitude",
        "x"
    ]

    y_dim = next((d for d in dims if d.lower() in y_map), None)
    x_dim = next((d for d in dims if d.lower() in x_map), None)

    # -------------------------
    # HARD FAIL if ambiguous
    # -------------------------
    if tile_dim is None:
        raise ValueError(f"No tile dim in {dims}")

    if y_dim is None:
        raise ValueError(f"No Y dim found in {dims}")

    if x_dim is None:
        raise ValueError(f"No X dim found in {dims}")

    if y_dim == x_dim:
        raise ValueError(f"Y and X resolved to same dim: {y_dim}")

    # -------------------------
    # RENAME
    # -------------------------
    da = da.rename({
        tile_dim: "tile",
        y_dim: "y",
        x_dim: "x"
    })

    # -------------------------
    # FINAL SAFETY CHECK
    # -------------------------
    da = da.transpose("tile", "y", "x")

    return da
