User Guide
==========

This guide explains how to use ``ufs_plot_utils`` to generate plots from:

- UFS/FV3 model outputs
- UFS-DA increment files
- Forecast datasets
- Restart files
- MOM6 ocean grids
- CICE sea-ice grids
- IODA observation files

Overview
--------

The package is organized into modular layers:

- ``Config``: YAML configuration loader
- ``Dataset``: Immutable dataset configuration object
- ``DataReader``: NetCDF/xarray I/O layer
- ``GeoReader``: Latitude/longitude handling
- ``PlotStyleResolver``: Colormap and range handling
- ``Plotter``: Cartopy/Matplotlib rendering
- ``Pipeline``: Workflow orchestration
- ``TaskBuilder``: Dynamic task generation

Installation
------------

Install into your Python environment:

.. code-block:: bash

   pip install -e .

Recommended dependencies:

.. code-block:: bash

   conda install cartopy xarray netcdf4 matplotlib pyyaml

Quick Start
-----------

1. Create a YAML configuration file.

2. Run the plotting pipeline:

.. code-block:: bash

   python -m ufs_plot_utils.cli_main \
       -i configs/config.yaml \
       -l INFO

3. Output figures will be written to:

.. code-block:: text

   ./

or the configured ``output.path``.

Configuration Structure
-----------------------

The workflow is fully YAML-driven.

Top-level structure:

.. code-block:: yaml

   input:
     parameters:
       cycle: t00z
       PDY: 20240224

     datasets:
       - name: example
         ...

   output:
     path: ./
     prefix: example

   plot:
     projection:
       name: Robinson

Datasets
--------

Each dataset defines:

- input files
- geometry source
- variables to plot
- styling information
- metadata

Example:

.. code-block:: yaml

   - name: fv3
     data_kind: increment

     geo:
       path: /path/to/geo
       filename: C96.mx100_oro_data
       file_type: orog

     data:
       path: /path/to/data
       filename: ufsda.t00z.atminc.cubed_sphere_grid
       file_type: tile
       var_list:
         - T_inc
         - u_inc

Supported Data Types
--------------------

Supported ``data_kind`` values:

- ``analysis``
- ``forecast``
- ``increment``
- ``restart``
- ``observation``
- ``single``

Supported Data Models
---------------------

Supported ``data_model`` values:

- ``fv3`` (default)
- ``mom6``
- ``cice``

Forecast Datasets
-----------------

Forecast files are automatically expanded using forecast hours.

Example:

.. code-block:: yaml

   filename: ufs.t00z.atmf*.tile1.nc

Detected forecast hours are used to generate independent plotting tasks.

Restart Datasets
----------------

Restart datasets support automatic restart-tag detection.

Example:

.. code-block:: yaml

   filename: '*.sfc_data.tile1.nc'

Observation Datasets
--------------------

IODA observation files are supported.

Features include:

- automatic lon/lat detection
- channel-aware plotting
- scatter visualization
- grouped NetCDF support

Example:

.. code-block:: yaml

   data_kind: observation

   data:
     group: ObsValue
     channels: [2, 7, 15]

Difference Plots
----------------

Difference tasks compute:

.. code-block:: text

   target - base

Example:

.. code-block:: yaml

   differences:
     - name: jedi-fv3
       base: fv3
       target: jedi

Features:

- symmetric ranges
- independent colormaps
- variable mapping support

Plot Configuration
------------------

Projection
^^^^^^^^^^

Supported projections:

- ``Robinson``
- ``PlateCarree``
- ``Mollweide``
- ``NorthPolarStereo``
- ``SouthPolarStereo``
- ``Stereographic``

Example:

.. code-block:: yaml

   projection:
     name: Robinson
     central_longitude: -77.0

Background Features
^^^^^^^^^^^^^^^^^^^

Supported background layers:

- ``coastline``
- ``borders``
- ``states``
- ``lakes``
- ``land``

Example:

.. code-block:: yaml

   background:
     features:
       - coastline
       - borders

Colormap and Range
^^^^^^^^^^^^^^^^^^

Per-variable styling is supported.

Example:

.. code-block:: yaml

   colormap:
     default: viridis
     T_inc: RdBu_r

   range:
     T_inc:
       vmin: -2.5
       vmax: 2.5

Automatic behavior:

- Increment and difference plots use symmetric scaling.
- Non-increment plots use percentile-based scaling.

Output Naming
--------------

Generated figures follow this convention:

.. code-block:: text

   <prefix>_<dataset>_<variable>_<z>_<date>_<cycle>.png

Example:

.. code-block:: text

   atmdata_fv3_T_inc_z076_20240224_t00z.png

Logging
-------

Set the logging level from the command line:

.. code-block:: bash

   python -m ufs_plot_utils.cli_main \
       -i config.yaml \
       -l DEBUG

Supported levels:

- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

Summary
-------

``ufs_plot_utils`` provides:

- modular plotting architecture
- YAML-driven workflows
- support for multiple UFS-related formats
- automated figure generation
- configurable styling and projections
