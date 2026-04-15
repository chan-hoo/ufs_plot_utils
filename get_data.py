import logging
from netCDF4 import Dataset
import numpy as np
import xarray as xr
import os

logger = logging.getLogger(__name__)

class GetData:
    """
    Read NetCDF data and extract 2D fields or 2D with tiles.
    """

    def __init__(self, cfg):
        self.cfg = cfg

        self.file_path = os.path.join(cfg.input_path, cfg.input_file)
        logger.info(f'''Opening dataset once: {self.file_path}''')
        try:
            self.ds = xr.open_dataset(self.file_path)
        except Exception as e:
            raise FileNotFoundError(f'''Could NOT open file: {self.file_path}''') from e


    def close(self):
        self.ds.close()


# ======================================================================================= CHJ =====
    def get_data_file(self, varname, z_index=None, time_index=0):
        """
        Extract 2D or 2D+tile data for a given variable from a single NetCDF file.
        """
        logger.info(f'''Reading variable: {varname}''')
        z_index = z_index if z_index is not None else getattr(self.cfg, "z_index", 0)

        da = self.ds[varname]

        logger.info(f'''{varname}:: dims = {da.dims}''')
        logger.info(f'''{varname}:: shape = {da.shape}''')

        # Extract info for the selected variable
        varname_long = da.attrs.get("long_name", "No long-name attribute found")
        varname_unit = da.attrs.get("units", "No units attribute found")
        var_cbar_label = f'''{varname_long} ({varname_unit})'''
        logger.info(f'''{varname}:: long name = {varname_long}''')
        logger.info(f'''{varname}:: unit = {varname_unit}''')
        logger.info(f'''{varname}:: cbar_label = {var_cbar_label}''')

        # Select time dimension if exists ("time" or "Time")
        time_dim = next((d for d in ["time", "Time"] if d in da.dims), None)
        if time_dim:
            if da.sizes[time_dim] > 1:
                logger.warning(f'''{time_dim} dimension > 1, using first index''')
            da = da.isel({time_dim: time_index})

        # Select vertical level if exists
        # pfull (1->127: high->low altitude: 127=near-surface, 76=505.65mb)
        z_dims = ["pfull", "zaxis_1", "zaxis_2", "zaxis_3", "zaxis_4", "lev", "level", "depth", "z"]        
        z_dim = next((d for d in z_dims if d in da.dims), None)
        if z_dim:
            logger.debug(f'''Using {z_dim} index = {z_index}''')
            da = da.isel({z_dim: z_index})

        # Ensure 2D or 2D with 6 tiles
        if "tile" in da.dims:
            if da.ndim != 3:
                raise ValueError(f'''{varname} is not 2D + tile after slicing, dims={da.dims}''')
            logger.info(f'''{varname} is 2D + tile, dims={da.dims}''')
        else:
            if da.ndim != 2:
                raise ValueError(f'''{varname} is not 2D after slicing, dims={da.dims}''')

        # Handle NaNs
        data_var = da.to_numpy()
        logger.info(f'''{varname}:: final shape = {data_var.shape}''')

        # Compute min/max excluding NaN
        data_min = np.nanmin(data_var)
        data_max = np.nanmax(data_var)
        logger.info(f'''{varname}:: min = {data_min}''')
        logger.info(f'''{varname}:: max = {data_max}''')

        return data_var, var_cbar_label, data_min, data_max


# ======================================================================================= CHJ =====
    def get_data_tiles(self):
        """
        Get metadata from multiple tiled files.
        Example) FV3: six tiles for the global domain.
        """


# ======================================================================================= CHJ =====
    def get_data_comp(self):
        """
        Get metadata from two files and set the difference between them.
        """



# ======================================================================================= CHJ =====
    def get_geo_file(self):
        """
        Extract latitude and longitude arrays.
        """    
        use_input_geo = str(getattr(self.cfg, "INPUT_HAS_GEO", "YES")).upper()
        if use_input_geo == "YES":
            logger.info(f'''Using input file for geo data''')
            ds_geo = self.ds
        else:
            geo_path = os.path.join(self.cfg.geo_path, self.cfg.geo_file)
            logger.info(f'''Opening separate geo file: {geo_path}''')
            try:
                ds_geo = xr.open_dataset(geo_path)
            except Exception as e:
                raise FileNotFoundError(f'''Could NOT open geo file: {geo_path}''') from e
    
        # Detect lat/lon variable names
        lat_candidates = ["lat", "latitude"]
        lon_candidates = ["lon", "longitude"]
    
        lat_name = next((v for v in lat_candidates if v in ds_geo.variables), None)
        lon_name = next((v for v in lon_candidates if v in ds_geo.variables), None)
    
        if lat_name is None or lon_name is None:
            raise ValueError(f'''Could not find lat/lon variables in dataset or check candidate lists''')
    
        logger.info(f'''Using lat variable: {lat_name}''')
        logger.info(f'''Using lon variable: {lon_name}''')
    
        lat = ds_geo[lat_name]
        lon = ds_geo[lon_name]
    
        logger.info(f"lat:: dims = {lat.dims}, shape = {lat.shape}")
        logger.info(f"lon:: dims = {lon.dims}, shape = {lon.shape}")
    
        # Convert to numpy
        lat = lat.to_numpy()
        lon = lon.to_numpy()
    
        return lat, lon


# ======================================================================================= CHJ =====
    def get_geo_orog(self):
        """
        Get longitudes and latitudes of the plotting target grid from a orography file.
        """

