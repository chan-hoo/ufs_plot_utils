Developer Guide
===============

This document describes the internal architecture and extension patterns used
throughout ``ufs_plot_utils``.

Architecture
------------

The package follows a layered architecture:

.. code-block:: text

   YAML Config
        ↓
      Config
        ↓
      Dataset
        ↓
      Pipeline
        ↓
    TaskBuilder
        ↓
      Tasks
        ↓
   Readers / Plotter
        ↓
      Output

Core Design Principles
----------------------

- Single responsibility per class
- YAML-driven behavior
- Stateless task execution
- Explicit configuration
- Reusable plotting and I/O layers

Core Components
---------------

Config
^^^^^^

``Config`` is a lightweight YAML wrapper.

Responsibilities:

- YAML loading
- nested key lookup
- configuration logging

Dataset
^^^^^^^

``Dataset`` is an immutable configuration object.

Responsibilities:

- flatten nested YAML sections
- validate dataset configuration
- expose standardized metadata

DataReader
^^^^^^^^^^

Handles all xarray/NetCDF data access.

Features:

- tiled FV3 datasets
- forecast detection
- restart-tag detection
- observation groups
- lazy loading

Important methods:

- ``get_data()``
- ``detect_forecast_hours()``
- ``detect_restart_tags()``
- ``resolve_filenames_for_fhr()``

GeoReader
^^^^^^^^^

Provides geographic coordinates.

Supports:

- FV3 orography tiles
- tiled forecast grids
- MOM6 staggered grids
- CICE staggered grids
- observation metadata

PlotStyleResolver
^^^^^^^^^^^^^^^^^

Centralized styling logic.

Responsibilities:

- colormap resolution
- value range resolution
- label generation
- automatic scaling

Important behavior:

- increments use symmetric scaling
- differences force symmetric ranges
- meteorological colormap heuristics

Plotter
^^^^^^^

Handles all rendering.

Plot types:

- ``plot_data_tiles()``
- ``plot_data_grid()``
- ``plot_data_scatter()``

Projection support:

- Robinson
- PlateCarree
- Mollweide
- Stereographic
- Polar stereographic

Pipeline
^^^^^^^^

The ``Pipeline`` class orchestrates execution.

Execution flow:

1. Load configuration
2. Build datasets
3. Build tasks
4. Read data
5. Resolve styles
6. Generate plots
7. Save output

Task System
-----------

The package uses task-based execution.

BaseTask
^^^^^^^^

Abstract interface:

.. code-block:: python

   class BaseTask:
       def run(self):
           raise NotImplementedError

PlotTask
^^^^^^^^

Handles a single plotting unit.

Responsibilities:

- data reading
- channel slicing
- title generation
- plotting
- output saving

DifferenceTask
^^^^^^^^^^^^^^

Handles:

- base dataset plotting
- target dataset plotting
- target-base difference plotting

Important:

- uses independent style resolvers
- forces symmetric difference scaling

TaskBuilder
^^^^^^^^^^^

Generates tasks dynamically based on:

- forecast hours
- restart tags
- observation channels
- dataset variables

Extension Patterns
------------------

Adding a New Data Type
^^^^^^^^^^^^^^^^^^^^^^

1. Add a new ``data_kind``.
2. Extend ``DataReader.get_data()``.
3. Add any required filename handling.
4. Update ``TaskBuilder`` if necessary.

Example:

.. code-block:: python

   elif self.data.data_kind == "my_new_type":
       return self._get_data_my_new_type(varname)

Adding a New Plot Type
^^^^^^^^^^^^^^^^^^^^^^

1. Add plotting logic to ``Plotter``.
2. Add dispatch logic in ``PlotTask.run()``.

Adding a New Projection
^^^^^^^^^^^^^^^^^^^^^^^

Extend ``Plotter.build_projection()``.

Example:

.. code-block:: python

   proj_map["LambertConformal"] = ccrs.LambertConformal

Supporting Additional File Formats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extend ``DataReader`` to support:

- zarr
- GRIB
- cloud storage backends
- alternative engines

Common Pitfalls
---------------

Shared Plotter State
^^^^^^^^^^^^^^^^^^^^

Always assign a resolver before plotting:

.. code-block:: python

   plotter.set_style_resolver(
       PlotStyleResolver(dataset)
   )

Dimension Mismatches
^^^^^^^^^^^^^^^^^^^^

Ensure:

.. code-block:: text

   lat.shape == data.shape

Tile Naming Assumptions
^^^^^^^^^^^^^^^^^^^^^^^

FV3 tiled datasets assume:

.. code-block:: text

   *.tile1.nc
   *.tile2.nc
   ...

Testing
-------

Recommended test coverage:

- ``DataReader``
- ``GeoReader``
- ``PlotStyleResolver``
- ``TaskBuilder``
- full pipeline smoke tests

Future Improvements
-------------------

Potential future enhancements:

- parallel task execution
- plugin system
- interactive plotting backends
- Dask integration
- cloud-native workflows
- stateless plotting API

Summary
-------

The package is designed to be:

- modular
- extensible
- configuration-driven
- task-oriented