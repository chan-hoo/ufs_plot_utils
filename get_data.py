import logging
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
        self.ds = None  # lazy initialization


    def _open_dataset(self):
        """
        Open dataset only when needed (lazy loading)
        """
        if self.ds is None:
            self.file_path = os.path.join(self.cfg.paths.input_path, self.cfg.filenames.input_file)
            logger.info(f"Opening dataset: {self.file_path}")
            try:
                self.ds = xr.open_dataset(self.file_path)
            except Exception as e:
                raise FileNotFoundError(f'''Could NOT open file: {self.file_path}''') from e


    def close(self):
        if self.ds is not None:
            self.ds.close()
            self.ds = None


# ======================================================================================= CHJ =====
    def get_data(self, varname, z_index=None, time_index=0):
        """
        Auto-detect tile vs single file
        """    
        if "tile" in self.ds.dims:
            return self.get_data_file(varname, z_index, time_index)
    
        # fallback: check tiled files exist
        try:
            return self.get_data_tiles(varname, z_index, time_index)
        except:
            return self.get_data_file(varname, z_index, time_index)


# ======================================================================================= CHJ =====
    def get_data_file(self, varname, z_index=None, time_index=0):
        """
        Extract 2D or 2D+tile data for a given variable from a single NetCDF file.
        """
        self._open_dataset()

        logger.info(f'''Reading variable: {varname}''')
        z_index = z_index if z_index is not None else getattr(self.cfg.params, "z_index", 0)

        da = self.ds[varname]

        logger.info(f'''{varname}:: dims = {da.dims}''')
        logger.debug(f'''{varname}:: shape = {da.shape}''')

        # Colorbar label
        var_cbar_label = self._build_cbar_label(da, varname)

        # Slice time and z-level
        da = self._slice_data(da, z_index, time_index)

        # Ensure 2D or 2D with 6 tiles
        if "tile" in da.dims:
            if da.ndim != 3:
                raise ValueError(f'''{varname} is not 2D + tile after slicing, dims={da.dims}''')
            logger.info(f'''{varname} is 2D + tile, dims={da.dims}''')
        else:
            if da.ndim != 2:
                raise ValueError(f'''{varname} is not 2D after slicing, dims={da.dims}''')

        logger.info(f'''{varname}:: final shape = {da.shape}''')

        return da, var_cbar_label


# ======================================================================================= CHJ =====
    def get_data_tiles(self, varname, z_index=None, time_index=0):
        """
        Read tiled NetCDF files using xarray (fast, lazy loading)
            input_file: prefix of input tiled files (Ex. {input_file}.tile#.nc)
        """    
        import re
        import glob
    
        input_file = getattr(self.cfg.filenames, "input_file")
        # Remove file extension
        base = os.path.splitext(input_file)[0]
        # Remove tile#
        if re.search(r'tile\d+$', base):
            prefix = re.sub(r'(tile)\d+$', r'\1', base)
        else:
            prefix = base
    
        input_path = getattr(self.cfg.paths, "input_path")
        z_index = z_index if z_index is not None else getattr(self.cfg.params, "z_index", 0)
    
        # Collect files
        pattern = os.path.join(input_path, f"{prefix}.tile*.nc")
        files = sorted(glob.glob(pattern))
    
        if len(files) != 6:
            raise ValueError(f'''Expected 6 tiles, found {len(files)}''')
    
        logger.info(f'''Opening tiled dataset (6 files)''')
    
        # Open all tiles at once
        ds = xr.open_mfdataset(
            files,
            combine="nested",
            concat_dim="tile"
        )
    
        if varname not in ds:
            raise ValueError(f'''{varname} not found in tiled dataset''')
    
        da = ds[varname]

        logger.info(f'''{varname}:: dims = {da.dims}''')
        logger.debug(f'''{varname}:: shape = {da.shape}''')
    
        # Slice time and z-level
        da = self._slice_data(da, z_index, time_index)

        # Ensure (tile, y, x)
        if da.ndim != 3:
            raise ValueError(f"{varname} is not (tile, y, x), dims={da.dims}")

        # Colorbar label
        var_cbar_label = self._build_cbar_label(da, varname)
    
        ds.close()
    
        return da, var_cbar_label


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
        use_input_geo = str(getattr(self.cfg.flags, "INPUT_HAS_GEO", "YES")).upper()
        if use_input_geo == "YES":
            logger.info(f'''Using input file for geo data''')
            self._open_dataset()
            ds_geo = self.ds
        else:
            geo_path = os.path.join(self.cfg.paths.geo_path, self.cfg.filenames.geo_file)
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
    
        logger.info(f'''lat:: dims = {lat.dims}, shape = {lat.shape}''')
        logger.info(f'''lon:: dims = {lon.dims}, shape = {lon.shape}''')
        
        return lat, lon


# ======================================================================================= CHJ =====
    def get_geo_orog(self):
        """
        Get longitudes and latitudes of the plotting target grid from a orography file.
        """



# ======================================================================================= CHJ =====
    def _slice_data(self, da, z_index, time_index):
        """
        Apply time + vertical slicing
        """    
        # time
        time_dim = next((d for d in ["time", "Time"] if d in da.dims), None)
        if time_dim:
            if da.sizes[time_dim] > 1:
                logger.warning(f"{time_dim} dimension > 1, using index {time_index}")
            da = da.isel({time_dim: time_index})
    
        # vertical
        # pfull (1->127: high->low altitude: 127=near-surface, 76=505.65mb)
        z_dims = ["pfull", "zaxis_1", "zaxis_2", "zaxis_3",
                  "zaxis_4", "lev", "level", "depth", "z"]
        z_dim = next((d for d in z_dims if d in da.dims), None)
        if z_dim:
            da = da.isel({z_dim: z_index})
    
        return da


    def _build_cbar_label(self, da, varname):
        """
        Build colorbar label + handle increment flag + logging.
        """    
        varname_long = da.attrs.get("long_name", "No long-name attribute found")
        varname_unit = da.attrs.get("units", "No units attribute found")
        logger.debug(f"{varname}:: long name = {varname_long}")
        logger.debug(f"{varname}:: unit = {varname_unit}")
   
        label = f"{varname_long} ({varname_unit})"
    
        # increment flag
        increment_flag = str(getattr(self.cfg.flags, "INCREMENT_PLOT", "NO")).upper()
        is_increment = increment_flag in ["YES", "TRUE", "1"]    
        if is_increment:
            label = f"Δ{label}"
    
        logger.info(f"{varname}:: cbar_label = {label}")
    
        return label

