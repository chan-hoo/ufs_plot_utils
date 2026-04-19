import os
import logging
import numpy as np
import xarray as xr
from .utils import extract_tile_prefix

logger = logging.getLogger(__name__)


class GeoReader:
    """
    Handle geographic data (lat/lon), supports file or tile format.
    """
    def __init__(self, geo_cfg):
        self.geo_cfg = geo_cfg

# ======================================================================================= CHJ =====
    def get_geo(self):
        """
        Choose geo data reading method based on config
        """
        geo_cfg = self.geo_cfg
        geo_type = geo_cfg.file_type.lower()

        if geo_type == "file":
            return self.get_geo_file()
        elif geo_type == "orog":
            return self.get_geo_orog()
        else:
            raise ValueError(f'''Unknown geo_file type: {geo_type}''')


# ======================================================================================= CHJ =====
    def get_geo_file(self):
        """
        Extract latitude and longitude arrays from input geo file.
        """
        geo_cfg = self.geo_cfg
        fpath = os.path.join(geo_cfg.path, geo_cfg.filename)
        logger.info(f'''Opening geo file: {fpath}''')
        try:
            ds_geo = xr.open_dataset(fpath)
        except Exception as e:
            raise FileNotFoundError(f'''Could NOT open geo file: {fpath}''') from e
    
        # Detect lat/lon variable names
        lat_candidates = ["lat", "latitude"]
        lon_candidates = ["lon", "longitude"]
    
        lat_name = next((v for v in lat_candidates if v in ds_geo.variables), None)
        lon_name = next((v for v in lon_candidates if v in ds_geo.variables), None)
    
        if lat_name is None or lon_name is None:
            raise ValueError(f'''Could not find lat/lon variables''')
    
        lat = ds_geo[lat_name]
        lon = ds_geo[lon_name]
    
        logger.info(f'''lat shape={lat.shape}, lon shape={lon.shape}''')
    
        ds_geo.close()
    
        return lat, lon


# ======================================================================================= CHJ =====
    def get_geo_orog(self):
        """
        Read 6 orography tile files and return lat/lon arrays:
            lat(tile, y, x), lon(tile, y, x)
        """
        geo_cfg = self.geo_cfg
        geo_file = geo_cfg.filename
        geo_path = geo_cfg.path

        # Remove file extension and tile#
        prefix = extract_tile_prefix(geo_file)
        logger.info(f'''OROG:: prefix = {prefix}''')
    
        lat_tiles = []
        lon_tiles = []
        for itile in range(1, 7):
            fname = f'''{prefix}.tile{itile}.nc'''
            fpath = os.path.join(geo_path, fname) 
            if not os.path.exists(fpath):
                raise FileNotFoundError(f'''Orography tile file not found: {fpath}''')
    
            logger.info(f'''Reading orography tile {itile}: {fpath}''')

            try:
                ds = xr.open_dataset(fpath)
            except Exception as e:
                raise FileNotFoundError(f'''Could NOT open {fpath}''') from e
    
            # Detect lat/lon names
            lat_name = next((v for v in ["geolat", "y", "lat", "latitude"] if v in ds.variables), None)
            lon_name = next((v for v in ["geolon", "x", "lon", "longitude"] if v in ds.variables), None)
    
            if lat_name is None or lon_name is None:
                raise ValueError(f'''lat/lon not found in {fpath}''')
    
            lat = ds[lat_name]
            lon = ds[lon_name]
            logger.debug(f'''Tile {itile} lat shape: {lat.shape}''')
            logger.debug(f'''Tile {itile} lon shape: {lon.shape}''')
    
            lat_tiles.append(lat)
            lon_tiles.append(lon)
    
            ds.close()
    
        # Stack: (tile, y, x)
        lat_all = np.stack(lat_tiles, axis=0)
        lon_all = np.stack(lon_tiles, axis=0)
    
        logger.info(f'''Geo lat shape: {lat_all.shape}''')
        logger.info(f'''Geo lon shape: {lon_all.shape}''')
    
        return lat_all, lon_all

