Python Packages
===============

When updating BYCEPS to a newer version, the set of required Python
packages may change (additions, version upgrades/downgrades, removals).

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation/virtual-env>` is set up and activated.

As with the :doc:`installation </installation/index>`, it's probably a
good idea to update pip_ to the current version:

.. _pip: https://pip.pypa.io/

.. code-block:: sh

    (venv)$ pip install --upgrade pip

Then instruct pip_ to install the required Python depdendencies (again,
the same way as during the installation):

.. code-block:: sh

    (venv)$ pip install -r requirements.txt

This will install new but yet missing packages and upgrade/downgrade
existing packages. It will *not* remove no longer used packages, though,
but that *should* not be an issue.

If you want to run the test suite and/or use development tools, update
their requirements as well:

.. code-block:: sh

    (venv)$ pip install -r requirements-dev.txt
