# Utility functions (not methods) used in multiple scripts
import logging
import os
import re

logger = logging.getLogger(__name__)


# =================================================================== CHJ ===

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


# =================================================================== CHJ ===

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


# =================================================================== CHJ ===

def normalize_geo_dims(lat, lon):
    """
    Normalize lat/lon to shape (tile, y, x)

    Accepts:
        - numpy arrays or xarray DataArray
        - 1D or 2D per tile
    """

    import numpy as np
    import xarray as xr

    # -------------------------
    # Convert to numpy
    # -------------------------
    if isinstance(lat, xr.DataArray):
        lat = lat.values
    if isinstance(lon, xr.DataArray):
        lon = lon.values

    # -------------------------
    # Ensure tile dimension exists
    # -------------------------
    if lat.ndim == 2:
        # single tile → promote
        lat = lat[np.newaxis, ...]
        lon = lon[np.newaxis, ...]

    if lat.ndim != 3:
        raise ValueError(
            f'''Geo must be 2D or 3D, got shape={lat.shape}'''
        )

    # -------------------------
    # Final safety check
    # -------------------------
    if lat.shape != lon.shape:
        raise ValueError(
            f'''lat/lon shape mismatch: {lat.shape} vs {lon.shape}'''
        )

    # -------------------------
    # Enforce (tile, y, x)
    # -------------------------
    # We assume last two dims are spatial (already true from your readers)
    # So just ensure ordering is correct (no-op for numpy)

    return lat, lon


# =================================================================== CHJ ===

def format_rtag(rtag):
    """
    Ensure format:
        YYYYMMDD.HH  (minimum)
    Trim trailing zeros beyond HH.
    """

    if "." not in rtag:
        return rtag

    date, time = rtag.split(".", 1)

    # Ensure at least HH exists
    if len(time) < 2:
        time = time.ljust(2, "0")

    hh = time[:2]
    rest = time[2:]

    # Trim trailing zeros ONLY from the rest
    rest = rest.rstrip("0")

    return f'''{date}.{hh}{rest}'''
