import os
import logging
import numpy as np
import xarray as xr
from .utils import (
    extract_tile_prefix,
    normalize_geo_dims,
    resolve_mom6_geo_vars,
    resolve_cice_geo_vars,
)

logger = logging.getLogger(__name__)


class GeoReader:
    """
    Handle geographic data (lat/lon), supports file or tile format.
    """
    def __init__(self, dataset):
        self.dataset = dataset

    # =============================================================== CHJ ===

    def get_geo(self, da=None):
        """
        Choose geo data reading method based on config
        """

        # Observation
        if self.dataset.data_kind == "observation":
            return self._get_geo_observation()

        # MOM6
        if self.dataset.data_model == "mom6":
            return self._get_geo_mom6(da)

        # CICE
        if self.dataset.data_model == "cice":
            return self._get_geo_cice(da)

        geo_type = self.dataset.geo_file_type.lower()
        if geo_type == "file":
            return self._get_geo_file()
        elif geo_type == "orog":
            return self._get_geo_orog()
        elif geo_type == "tile":
            return self._get_geo_tile()
        else:
            raise ValueError(f'''Unknown geo type: {geo_type}''')

    # =============================================================== CHJ ===

    def _get_geo_file(self):
        """
        Extract latitude and longitude arrays from input geo file.
        """

        fpath = os.path.join(
            self.dataset.geo_path,
            self.dataset.geo_filename
        )

        logger.info(f'''Opening geo file: {fpath}''')

        with xr.open_dataset(
            fpath,
            decode_timedelta=True,
        ) as ds_geo:
            # flatten groups
            ds_flat = xr.Dataset({k: v for k, v in ds_geo.data_vars.items()})
            lat_candidates = ["lat", "latitude"]
            lon_candidates = ["lon", "longitude"]

            lat_name = next((v for v in lat_candidates if v in ds_flat), None)
            lon_name = next((v for v in lon_candidates if v in ds_flat), None)

            if lat_name is None or lon_name is None:
                raise ValueError("Could not detect lon/lat in OBS file")

            lat = ds_flat[lat_name]
            lon = ds_flat[lon_name]

        # Handle 1D case
        if lat.ndim == 1 and lon.ndim == 1:
            lon2d, lat2d = np.meshgrid(lon.values, lat.values)
        else:
            lat2d = lat.values
            lon2d = lon.values

        # Normalize geo dimensions
        lat_all, lon_all = normalize_geo_dims(lat2d, lon2d)

        logger.info(f'''lat shape={lat.shape}, lon shape={lon.shape}''')

        return lat_all, lon_all

    # =============================================================== CHJ ===

    def _get_geo_orog(self):
        """
        Read 6 orography tile files and return lat/lon arrays:
            lat(tile, y, x), lon(tile, y, x)
        """

        geo_file = self.dataset.geo_filename
        geo_path = self.dataset.geo_path

        prefix = extract_tile_prefix(geo_file)
        logger.info(f'''OROG:: prefix = {prefix}''')

        lat_tiles = []
        lon_tiles = []

        for itile in range(1, 7):
            fname = f'''{prefix}.tile{itile}.nc'''
            fpath = os.path.join(geo_path, fname)

            if not os.path.exists(fpath):
                raise FileNotFoundError(
                    f'''Orography tile file not found: {fpath}'''
                )

            logger.info(f'''Reading orography tile {itile}: {fpath}''')

            with xr.open_dataset(
                fpath,
                decode_timedelta=True,
            ) as ds:
                lat_candidates = ["geolat", "y", "lat", "latitude"]
                lon_candidates = ["geolon", "x", "lon", "longitude"]
                lat_name = next(
                    (v for v in lat_candidates if v in ds.variables),
                    None,
                )
                lon_name = next(
                    (v for v in lon_candidates if v in ds.variables),
                    None,
                )

                if lat_name is None or lon_name is None:
                    raise ValueError(f'''lat/lon not found in {fpath}''')

                lat_tiles.append(ds[lat_name].values)
                lon_tiles.append(ds[lon_name].values)

        lat_all = np.stack(lat_tiles, axis=0)
        lon_all = np.stack(lon_tiles, axis=0)

        # Normalize geo dimensions
        lat_all, lon_all = normalize_geo_dims(lat_all, lon_all)

        logger.info(f'''Geo lat shape: {lat_all.shape}''')
        logger.info(f'''Geo lon shape: {lon_all.shape}''')

        return lat_all, lon_all

    # =============================================================== CHJ ===

    def _get_geo_tile(self):
        """
        Extract lat/lon from tiled data files (grid_xt/grid_yt or similar).
        Returns:
            lat(tile, y, x), lon(tile, y, x)
        """

        import glob
        import re

        geo_file = self.dataset.geo_filename
        geo_path = self.dataset.geo_path

        # -------------------------
        # Build tile file list
        # -------------------------
        prefix = extract_tile_prefix(geo_file)
        pattern = os.path.join(geo_path, f'''{prefix}.tile*.nc''')

        logger.info(f'''GEO TILE pattern: {pattern}''')

        file_list = sorted(glob.glob(pattern))
        if not file_list:
            raise ValueError(f'''No geo tile files found: {pattern}''')

        # -------------------------
        # Group by forecast hour
        # -------------------------
        fhr_map = {}
        for f in file_list:
            m = re.search(r'''\.f(\d{3})\.''', f)
            if m:
                fhr = m.group(1)
            else:
                fhr = "static"  # no forecast in filename

            fhr_map.setdefault(fhr, []).append(f)

        # -------------------------
        # Select one fhr (first)
        # -------------------------
        selected_fhr = sorted(fhr_map.keys())[0]
        selected_files = sorted(fhr_map[selected_fhr])

        logger.info(f'''Geo using forecast hour: {selected_fhr}''')

        if len(selected_files) != 6:
            raise ValueError(
                f'''Expected 6 tiles for f{selected_fhr}, '''
                f'''found {len(selected_files)}'''
            )

        # -------------------------
        # Read lat/lon
        # -------------------------
        lat_tiles = []
        lon_tiles = []

        for f in selected_files:
            logger.info(f'''Reading geo tile: {f}''')

            with xr.open_dataset(
                f,
                decode_timedelta=True,
            ) as ds:
                # -------------------------
                # Candidate variable names
                # -------------------------
                lat_candidates = ["grid_yt", "lat", "latitude", "y"]
                lon_candidates = ["grid_xt", "lon", "longitude", "x"]
                lat_name = next(
                    (v for v in lat_candidates if v in ds.variables),
                    None,
                )
                lon_name = next(
                    (v for v in lon_candidates if v in ds.variables),
                    None,
                )

                if lat_name is None or lon_name is None:
                    raise ValueError(f'''lat/lon not found in {f}''')

                lat = ds[lat_name]
                lon = ds[lon_name]

            # -------------------------
            # Handle 1D -> 2D mesh
            # -------------------------
            if lat.ndim == 1 and lon.ndim == 1:
                lon2d, lat2d = np.meshgrid(lon.values, lat.values)
            else:
                lat2d = lat.values
                lon2d = lon.values

            lat_tiles.append(lat2d)
            lon_tiles.append(lon2d)

        lat_all = np.stack(lat_tiles, axis=0)
        lon_all = np.stack(lon_tiles, axis=0)

        # Normalize geo dimensions
        lat_all, lon_all = normalize_geo_dims(lat_all, lon_all)

        logger.info(f'''Geo lat shape: {lat_all.shape}''')
        logger.info(f'''Geo lon shape: {lon_all.shape}''')

        return lat_all, lon_all

    # =============================================================== CHJ ===

    def _get_geo_mom6(self, da):

        fpath = os.path.join(
            self.dataset.geo_path,
            self.dataset.geo_filename
        )

        lon_name, lat_name = resolve_mom6_geo_vars(da)

        logger.info(
            f'''MOM6 grid mapping:: '''
            f'''{da.dims} -> {lon_name}/{lat_name}'''
        )

        with xr.open_dataset(
            fpath,
            decode_timedelta=True,
        ) as ds:
            lon = ds[lon_name].values
            lat = ds[lat_name].values

        return normalize_geo_dims(
            lat,
            lon,
            add_tile_dim=False,
        )

    # =============================================================== CHJ ===

    def _get_geo_cice(self, da):

        fpath = os.path.join(
            self.dataset.geo_path,
            self.dataset.geo_filename
        )

        lon_name, lat_name = resolve_cice_geo_vars(da)

        logger.info(
            f'''CICE grid mapping:: '''
            f'''{da.name} -> {lon_name}/{lat_name}'''
        )

        with xr.open_dataset(
                fpath,
                decode_timedelta=True,
        ) as ds:
            lon = ds[lon_name].values
            lat = ds[lat_name].values

        return normalize_geo_dims(
            lat,
            lon,
            add_tile_dim=False,
        )

    # =============================================================== CHJ ===

    def _get_geo_observation(self):
        """
        Read lon/lat from IODA-style observation file.

        Handles:
          - MetaData group (standard)
          - fallback to root
        """

        fpath = os.path.join(
            self.dataset.path,
            self.dataset.filename
        )

        logger.info(f'''Opening OBS geo file: {fpath}''')

        # -------------------------
        # 1. Try MetaData group (IODA standard)
        # -------------------------
        try:
            with xr.open_dataset(
                fpath,
                group="MetaData",
                decode_timedelta=True,
            ) as ds:
                logger.info("Trying group: MetaData")

                lon = ds["longitude"].values
                lat = ds["latitude"].values

                logger.info("Found lon/lat in MetaData group")
        except Exception as e:
            logger.warning(f'''MetaData group read failed: {e}''')

            # -------------------------
            # 2. Fallback: root
            # -------------------------
            with xr.open_dataset(
                fpath,
                decode_timedelta=True,
            ) as ds:
                logger.info("Falling back to ROOT group")

                lon_candidates = ["lon", "longitude"]
                lat_candidates = ["lat", "latitude"]
                lon_name = next(
                    (v for v in lon_candidates if v in ds.variables),
                    None,
                    )
                lat_name = next(
                    (v for v in lat_candidates if v in ds.variables),
                    None,
                )

                if lon_name is None or lat_name is None:
                    raise ValueError("Could not detect lon/lat in OBS file")

                lon = ds[lon_name].values
                lat = ds[lat_name].values

        # -------------------------
        # Validation
        # -------------------------
        if lon.ndim != 1 or lat.ndim != 1:
            raise ValueError("Observation lon/lat must be 1D")

        if lon.shape != lat.shape:
            raise ValueError("lon/lat shape mismatch")

        logger.info(f'''OBS geo size = {lon.size}''')

        return lat, lon
