Python Packages
===============

When updating BYCEPS to a newer version, the set of required Python
packages may change (additions, version upgrades/downgrades, removals).

Instruct uv to install the required Python dependencies (the same way as
during the installation):

.. code-block:: console

    $ uv sync --frozen

This will install new but yet missing packages, upgrade/downgrade
existing packages, and remove no longer required packages.

If you want to use development tools, update their dependencies as well:

.. code-block:: console

    $ uv sync --frozen --group dev
