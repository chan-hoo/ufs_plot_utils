import logging
import numpy as np
import xarray as xr
import os
import glob
import re
from .utils import extract_tile_prefix

logger = logging.getLogger(__name__)

class DataReader:
    """
    Read NetCDF data and extract fields (I/O layer only).
    """
    def __init__(self, data):
        # -------------------------
        # Config (immutable)
        # -------------------------
        self.data = data

        self.path = data.path
        self.filename = data.filename
        self.file_type = data.file_type

        self.z_index = data.z_index
        self.time_index = data.time_index

        # -------------------------
        # Runtime (xarray dataset)
        # -------------------------
        self.xr_ds = None


# ======================================================================================= CHJ =====
    def _open_dataset(self):
        """
        Open dataset only when needed (lazy loading)
        """
        if self.xr_ds is None:
            file_path = os.path.join(self.path, self.filename)

            logger.info(f'''Opening data: {file_path}''')

            self.xr_ds = xr.open_dataset(file_path, engine="netcdf4")


# ======================================================================================= CHJ =====
    def get_data(self, varname, fhr=None, rtag=None):
        """
        Return raw DataArray (NO styling, NO plotting logic).
        """
        logger.debug(f'''data file type = {self.file_type}''')

        # -------------------------
        # FORECAST
        # -------------------------
        if self.data.data_kind == "forecast":
            if fhr is None:
                raise ValueError(f'''Forecast data requires fhr''')
        
            files = self.resolve_filenames_for_fhr(fhr)
        
            if self.file_type == "tile":
                return self._get_data_tiles(varname, files)
            elif self.file_type == "file":
                return self._get_data_file(varname, files)
            else:
                raise ValueError(f'''Unsupported file_type: {self.file_type}''')
        
        # -------------------------
        # RESTART
        # -------------------------
        elif self.data.data_kind == "restart":
            if rtag is None:
                raise ValueError(f'''Restart data requires rtag''')
        
            files = self.resolve_filenames_for_restart(rtag)
        
            if self.file_type == "tile":
                return self._get_data_tiles(varname, files)
            elif self.file_type == "file":
                return self._get_data_file(varname, files)
            else:
                raise ValueError(f'''Unsupported file_type: {self.file_type}''')
        
        # -------------------------
        # DEFAULT
        # -------------------------
        else:
            if self.file_type == "tile":
                return self._get_data_tiles(varname)
        
            elif self.file_type == "file":
                return self._get_data_file(varname)
        
            else:
                raise ValueError(f'''Unsupported file_type: {self.file_type}''')


# ======================================================================================= CHJ =====
    def _get_data_file(self, varname):
        """
        Read single NetCDF file and return DataArray.
        """    
        self._open_dataset()
    
        logger.info(f'''Reading variable: {varname}''')
    
        if varname not in self.xr_ds:
            raise ValueError(f'''{varname} not found in dataset''')
    
        da = self.xr_ds[varname]
    
        logger.debug(f'''{varname} dims = {da.dims}''')
        logger.debug(f'''{varname} shape = {da.shape}''')
    
        # apply slicing (data-layer only)
        da = self._slice_data(da, self.z_index, self.time_index)

        # -------------------------
        # validation
        # -------------------------
        if "tile" in da.dims:
            if da.ndim != 3:
                raise ValueError(f'''{varname} expected (tile,y,x), got {da.dims}''')
        else:
            if da.ndim != 2:
                raise ValueError(f'''{varname} expected 2D, got {da.dims}''')
    
        logger.info(f'''{varname} final shape = {da.shape}''')
        logger.info(f'''{varname} min={np.nanmin(da.values)}, max={np.nanmax(da.values)}''')
    
        return da


# ======================================================================================= CHJ =====
    def _get_data_tiles(self, varname, files=None):
        """
        Read 6-tile NetCDF and return DataArray (tile, y, x).
        """    
        # -------------------------
        # FORECAST: files already resolved
        # -------------------------
        if files is not None:
            if len(files) != 6:
                raise ValueError(f'''Expected 6 tiles, found {len(files)}''')
            logger.debug(f'''Tile files: {files}''')
    
        # -------------------------
        # INCREMENT / ANALYSIS: use prefix
        # -------------------------
        else:
            prefix = extract_tile_prefix(self.filename)
            pattern = os.path.join(self.path, f'''{prefix}.tile*.nc''')
            logger.debug(f'''Tile pattern: {pattern}''')
    
            files = sorted(glob.glob(pattern))
            if len(files) != 6:
                raise ValueError(f'''Expected 6 tiles, found {len(files)}''')
            logger.debug(f'''Files found: {files}''')
    
        # -------------------------
        # COMMON PROCESSING
        # -------------------------
        logger.info(f'''Opening 6 tiles for variable: {varname}''')
        datasets = []
        try:
            for f in files:
                datasets.append(xr.open_dataset(f))
    
            ds = xr.concat(datasets, dim="tile")
    
            if varname not in ds:
                raise ValueError(f'''{varname} not found in tiled dataset''')
    
            da = ds[varname]
    
            logger.debug(f'''{varname} dims = {da.dims}''')
            logger.debug(f'''{varname} shape = {da.shape}''')

            da = self._slice_data(da, self.z_index, self.time_index)
    
            if da.ndim != 3:
                raise ValueError(f'''{varname} expected (tile, y, x), got {da.dims}''')
    
            vals = da.values
            logger.info(f'''{varname} final shape = {da.shape}''')
            logger.info(f'''{varname} min={np.nanmin(vals)}, max={np.nanmax(vals)}''')
    
            return da
    
        finally:
            for d in datasets:
                try:
                    d.close()
                except Exception:
                    pass


# ======================================================================================= CHJ =====
    def _slice_data(self, da, z_index=None, time_index=0):
        """
        Apply time + vertical slicing (data-layer only).
        """ 
        # -------------------------
        # time slicing
        # -------------------------
        time_dim = next((d for d in ["time", "Time"] if d in da.dims), None)
        if time_dim is not None:
            if da.sizes.get(time_dim, 1) > 1:
                logger.debug(f'''{time_dim} > 1, selecting index {time_index}''')
            da = da.isel({time_dim: time_index})
    
        # -------------------------
        # vertical slicing
        # -------------------------
        z_dims = [
            "pfull", "zaxis_1", "zaxis_2", "zaxis_3",
            "zaxis_4", "lev", "level", "depth", "z"
        ]
    
        z_dim = next((d for d in z_dims if d in da.dims), None)
    
        if z_dim is not None and z_index is not None:
            da = da.isel({z_dim: z_index})
    
        return da


# ======================================================================================= CHJ =====
    def detect_forecast_hours(self):
        """
        Detect forecast hours from filename pattern.
        Works for:
          - f*
          - any glob pattern containing fXXX
        """
        pattern = self.filename
        # Convert pattern to glob
        glob_pattern = pattern
    
        # If user used [1-6], reduce to tile1 for detection
        glob_pattern = re.sub(r"\[1-6\]", "1", glob_pattern)
        search_path = os.path.join(self.path, glob_pattern)
        logger.info(f'''Detecting forecast files: {search_path}''')
    
        files = glob.glob(search_path)
        if not files:
            raise ValueError(f'''No files found for pattern: {search_path}''')
    
        fhrs = set() 
        for f in files:
            fname = os.path.basename(f)
            # robust match: f000, f012, f120 etc.
            match = re.search(r"\.f(\d{2,4})\.", fname)
            if match:
                fhrs.add(match.group(1))
    
        if not fhrs:
            raise ValueError("Could not detect forecast hours from filenames")
    
        fhrs = sorted(fhrs)
    
        logger.info(f'''Detected forecast hours: {fhrs}''')
    
        return fhrs


# ======================================================================================= CHJ =====
    def resolve_filenames_for_fhr(self, fhr):
        """
        Return list of matching files for a given forecast hour.
        """   
        # -------------------------
        # Replace wildcard with fhr
        # -------------------------
        pattern = self.filename.replace("*", fhr)
    
        # -------------------------
        # Detect tile pattern
        # -------------------------
        if "tile1" in pattern:
            files = [
                os.path.join(
                    self.path,
                    pattern.replace("tile1", f'''tile{i}''')
                )
                for i in range(1, 7)
            ]
    
        elif "tile" in pattern:
            # handle generic "tile" case
            files = [
                os.path.join(
                    self.path,
                    re.sub(r'''tile\d+''', f'''tile{i}''', pattern)
                )
                for i in range(1, 7)
            ]
    
        else:
            raise ValueError(f'''Cannot resolve tile pattern from: {pattern}''')
    
        # -------------------------
        # Validate existence (important)
        # -------------------------
        missing = [f for f in files if not os.path.exists(f)]
        if missing:
            raise FileNotFoundError(
                f'''Missing tile files for f{fhr}: {missing}'''
            )
    
        return files


# ======================================================================================= CHJ =====
    def detect_restart_tags(self):
    
        pattern = os.path.join(self.path, self.filename)
        files = glob.glob(pattern)
    
        if not files:
            raise ValueError(f'''No restart files found: {pattern}''')
    
        tags = set()
    
        for f in files:
            base = os.path.basename(f)
    
            # match leading timestamp like 20250121.000000
            m = re.match(r'''(\d{8}\.\d{6})''', base)
            if m:
                tags.add(m.group(1))
            else:
                # fallback: grab HHMM before ".sfc_data"
                m2 = re.search(r'''(\d{4})\.sfc_data''', base)
                if m2:
                    tags.add(m2.group(1))
    
        tags = sorted(tags)
    
        logger.info(f'''Detected restart tags: {tags}''')
    
        return tags


# ======================================================================================= CHJ =====
    def resolve_filenames_for_restart(self, tag):
    
        pattern = self.filename.replace("*", tag)
    
        if "tile1" in pattern:
            files = [
                os.path.join(
                    self.path,
                    pattern.replace("tile1", f'''tile{i}''')
                )
                for i in range(1, 7)
            ]
        else:
            raise ValueError(f'''Invalid restart tile pattern: {pattern}''')
    
        return files


# ======================================================================================= CHJ =====
    def close(self):
        if self.xr_ds is not None:
            try:
                self.xr_ds.close()
            finally:
                self.xr_ds = None
