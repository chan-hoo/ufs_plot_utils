User Guide
==========

This guide explains how to use the UFS-DA plotting pipeline to generate
visualizations from model, analysis, forecast, restart, and observation datasets.

Overview
--------

The pipeline is designed with a clear separation of responsibilities:

- **Configuration**: YAML-driven setup
- **Data I/O**: NetCDF/xarray-based readers
- **Processing**: Task-based pipeline execution
- **Visualization**: Cartopy + Matplotlib
- **Output**: Automated figure naming and saving

Main components:

- ``Pipeline``: Orchestrates the workflow
- ``Dataset``: Defines input data and metadata
- ``DataReader``: Reads variables from files
- ``GeoReader``: Provides latitude/longitude grids
- ``Plotter``: Generates figures
- ``OutputManager``: Saves figures
- ``PlotStyleResolver``: Controls colormap, range, and labels

---

Quick Start
-----------

1. Prepare a YAML configuration file:

.. code-block:: bash

   cd configs
   cp config_[case].yaml config.yaml

2. Run the pipeline:

.. code-block:: bash

   python run_plot_task.py
   (or python run_plot_task.py -i config_[case].yaml -l INFO)

3. Output figures will be saved to:

.. code-block:: text

   ./ (or configured output path)

---

YAML Configuration
------------------

The entire pipeline is controlled via a YAML file.

Top-level structure:

.. code-block:: yaml

   input:
     parameters:
       cycle: t00z
       PDY: 20240224

     datasets:
       - name: dataset_name
         ...

   output:
     path: ./
     prefix: atmdata

   plot:
     ...

---

Datasets
--------

Each dataset defines:

- Data source
- Geometry source
- Variables to plot
- Plot styling

Example:

.. code-block:: yaml

   - name: fv3
     data_kind: increment

     geo:
       path: /path/to/geo
       filename: geo_file
       file_type: orog

     data:
       path: /path/to/data
       filename: file_pattern
       file_type: tile
       var_list:
         - T_inc
         - u_inc
         - v_inc
       z_index: 76

---

Data Types
----------

Supported ``data_kind`` values:

- ``analysis``
- ``forecast``
- ``increment``
- ``restart``
- ``observation``

Each type affects how files are read and processed.

---

File Types
----------

Supported ``file_type``:

- ``file``: Single NetCDF file
- ``tile``: Cubed-sphere tiled files (6 tiles)
- ``orog``: Orography tiles (for geo)

---

Colormap and Range
------------------

You can define per-variable styling:

.. code-block:: yaml

   colormap:
     default: viridis
     T_inc: RdBu_r

   range:
     default:
       vmin: null
       vmax: null
     T_inc:
       vmin: -2.5
       vmax: 2.5

Behavior:

- If not specified → automatic percentile-based scaling
- Difference plots → symmetric range enforced

---

Forecast Data
-------------

Forecast datasets must include a filename pattern:

.. code-block:: yaml

   filename: ufs.t00z.atmf*.tile1.nc

The pipeline automatically detects forecast hours (``fhr``).

---

Restart Data
------------

Restart datasets use time tags:

.. code-block:: yaml

   filename: *.tile1.nc

Tags are automatically detected (e.g., ``20240224.000000``).

---

Observation Data
----------------

Supports IODA-style observation files.

Features:

- Automatic lat/lon detection
- Channel-aware plotting
- Scatter visualization

Example:

.. code-block:: yaml

   data_kind: observation
   channels: [1, 2, 3]

---

Plot Configuration
------------------

Control figure appearance:

.. code-block:: yaml

   plot:
     projection:
       name: Robinson
       central_longitude: -77.0

     figure:
       figsize: [5, 2.5]
       dpi: 300

     colorbar:
       extend: both

     background:
       features:
         - coastline

Supported projections:

- ``Robinson``
- ``PlateCarree``
- ``Mollweide``

---

Output
------

Output files are automatically named:

.. code-block:: text

   <prefix>_<dataset>_<variable>_<z>_<date>_<cycle>.png

Example:

.. code-block:: text

   atmdata_fv3_T_inc_z076_20240224_t00z.png

---

Difference Plots
----------------

You can define differences between datasets:

.. code-block:: yaml

   input:
     differences:
       - name: fv3_minus_jedi
         base: fv3
         target: jedi
         var_pairs:
           - base: T_inc
             target: tmp

Features:

- Computes: ``target - base``
- Uses symmetric color range
- Supports custom colormap and range

---

Execution Flow
--------------

1. Load configuration
2. Initialize datasets
3. Build tasks
4. Read data
5. Resolve styles
6. Generate plots
7. Save outputs

---

Logging
-------

Set logging level via CLI:

.. code-block:: bash

   python run_plot_task.py -i config.yaml -l DEBUG

Available levels:

- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

---

Advanced Usage
--------------

You can extend the pipeline by:

- Adding new ``data_kind`` handlers
- Customizing ``PlotStyleResolver``
- Creating new task types
- Supporting new projections

---

Summary
-------

This pipeline provides:

- Modular architecture
- YAML-driven configuration
- Support for multiple data formats
- Automated plotting workflow
- Flexible styling system

For more details, refer to the API documentation.
