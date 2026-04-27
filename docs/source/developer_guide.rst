Developer Guide
===============

This guide describes the internal architecture, execution flow, and extension
patterns of the plotting pipeline. It is intended for contributors who want to
add features, support new data formats, or modify behavior safely.

Contents
--------

.. contents::
   :local:
   :depth: 2

Architecture Overview
---------------------

The system follows a modular, layered design:

- **Configuration Layer**: YAML → ``Config``
- **Domain Model**: ``Dataset``
- **I/O Layer**: ``DataReader``, ``GeoReader``
- **Processing Layer**: ``TaskBuilder``, ``PlotTask``, ``DifferenceTask``
- **Styling Layer**: ``PlotStyleResolver``
- **Rendering Layer**: ``Plotter``
- **Output Layer**: ``OutputManager``

Key principle: **separation of concerns + task-based execution**.

Execution Flow
--------------

High-level sequence:

1. Load YAML → ``Config``
2. Build ``Dataset`` objects
3. Initialize ``Pipeline``
4. Build tasks via ``TaskBuilder``
5. Execute tasks:
   - Read data
   - Resolve style
   - Plot
   - Save output

Core Classes
------------

Pipeline
^^^^^^^^

- Entry point for execution
- Holds shared services:
  - ``Plotter``
  - ``OutputManager``
  - ``NameBuilder``

Methods:

- ``run_plot_tiles()``
- ``run_differences()``

Dataset
^^^^^^^

Immutable configuration object.

Responsibilities:

- Normalize YAML structure
- Provide unified access to:
  - paths
  - file types
  - variables
  - styling config

Design note:
- Keep it **lightweight and validation-focused**

DataReader
^^^^^^^^^^

Handles all **data I/O** using xarray.

Responsibilities:

- Open datasets (lazy)
- Slice dimensions (time, vertical)
- Handle:
  - tiled data
  - forecast patterns
  - restart tags
  - observations

Extension point:
- Add new ``data_kind`` behaviors here

GeoReader
^^^^^^^^^

Provides latitude/longitude grids.

Supports:

- file-based geo
- orography tiles
- tiled data
- observation files

Important invariant:

.. code-block:: text

   lat.shape == data.shape

PlotStyleResolver
^^^^^^^^^^^^^^^^^

Centralized styling logic:

- colormap
- value range
- label generation

Design:

- Config-driven (YAML)
- Fallback to heuristics
- Special handling for differences

Important behavior:

- Increment/difference → symmetric range
- Auto-scaling via percentiles

Plotter
^^^^^^^

Responsible for rendering using Cartopy + Matplotlib.

Key methods:

- ``plot_data_tiles()``
- ``plot_data_scatter()``

Important:

- Requires a **style resolver per task**
- Uses config-driven projection and layout

OutputManager
^^^^^^^^^^^^^

Handles:

- output directory creation
- filename normalization
- figure saving

Task System
-----------

The pipeline uses a **task-based execution model**.

BaseTask
^^^^^^^^

Abstract class:

.. code-block:: python

   class BaseTask:
       def run(self):
           raise NotImplementedError

PlotTask
^^^^^^^^

Represents a single plotting unit.

Responsibilities:

- Read data
- Apply slicing/context (fhr, rtag, channel)
- Generate title and filename
- Call Plotter
- Save output

Important pattern:

.. code-block:: python

   # MUST set resolver per task
   plotter.set_style_resolver(PlotStyleResolver(dataset))

DifferenceTask
^^^^^^^^^^^^^^

Handles dataset comparison:

- Computes: ``target - base``
- Plots:
  1. base
  2. target
  3. difference

Uses:

- independent resolvers per phase
- symmetric scaling for difference

TaskBuilder
^^^^^^^^^^^

Generates tasks dynamically based on:

- ``data_kind``
- forecast hours
- restart tags
- observation channels

Design:

- No execution logic
- Pure task construction

Extension Patterns
------------------

Adding a New Data Type
^^^^^^^^^^^^^^^^^^^^^^

1. Extend ``Dataset.data_kind``

2. Add logic in ``DataReader.get_data()``:

.. code-block:: python

   elif self.data.data_kind == "my_new_type":
       return self._get_data_my_new_type(varname)

3. Implement reader method

4. Update ``TaskBuilder`` if needed

---

Adding a New Plot Type
^^^^^^^^^^^^^^^^^^^^^^

1. Add method to ``Plotter``:

.. code-block:: python

   def plot_my_new_type(...):
       ...

2. Call it in ``PlotTask.run()`` based on condition

---

Custom Colormap Logic
^^^^^^^^^^^^^^^^^^^^^

Modify:

- ``PlotStyleResolver._resolve_cmap``

Example:

.. code-block:: python

   if "humidity" in varname:
       cmap = plt.get_cmap("Blues")

---

Custom Range Logic
^^^^^^^^^^^^^^^^^^

Modify:

- ``_resolve_range``

Example:

- percentile thresholds
- log scaling
- fixed bounds

---

Adding New Background Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Modify:

- ``Plotter.plot_background``

Example:

.. code-block:: python

   if "rivers" in features:
       ax.add_feature(cfeature.RIVERS)

---

Supporting New File Formats
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extend ``DataReader``:

- Add new open logic
- Possibly new engine (e.g., zarr)

---

Design Principles
-----------------

1. **Single Responsibility**
   - Each class does one thing

2. **Config-Driven**
   - Avoid hardcoding behavior

3. **Stateless Tasks**
   - Tasks must not depend on shared mutable state

4. **Fail Fast**
   - Validate early (shapes, variables)

5. **Explicit over Implicit**
   - Avoid hidden magic

---

Common Pitfalls
---------------

Shared Plotter State
^^^^^^^^^^^^^^^^^^^^

Do NOT rely on global resolver state.

Always set resolver per task:

.. code-block:: python

   plotter.set_style_resolver(PlotStyleResolver(dataset))

---

Geo/Data Mismatch
^^^^^^^^^^^^^^^^^

Ensure:

.. code-block:: text

   lat.shape == data.shape

---

Variable Name Mismatch
^^^^^^^^^^^^^^^^^^^^^^

YAML keys must match dataset variable names exactly.

---

Tile Dimension Issues
^^^^^^^^^^^^^^^^^^^^^

Use:

- ``normalize_tile_dims``

---

Pipeline Flow Diagram
---------------------

.. mermaid::

   flowchart TD
       A[Config YAML] --> B[Config]
       B --> C[Dataset Objects]

       C --> D[Pipeline]
       D --> E[TaskBuilder]

       E --> F[PlotTask]
       E --> G[DifferenceTask]

       F --> H[DataReader]
       F --> I[GeoReader]
       F --> J[PlotStyleResolver]
       F --> K[Plotter]
       F --> L[OutputManager]

       G --> H
       G --> I
       G --> J
       G --> K
       G --> L

       H --> K
       I --> K
       J --> K

       K --> L

---

Testing Strategy
----------------

Recommended tests:

- DataReader (file + tile + obs)
- GeoReader (all modes)
- PlotStyleResolver (range + cmap)
- TaskBuilder (correct task counts)

---

Future Improvements
-------------------

- Stateless Plotter API (pass resolver directly)
- Parallel task execution
- Plugin system for new data types
- Interactive visualization backend

---

Summary
-------

The pipeline is:

- modular
- extensible
- config-driven
- task-oriented

Understanding the **task system + style resolver** is key to extending it safely.
