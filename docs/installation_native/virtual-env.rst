Set Up a Virtual Python Environment
===================================

The installation should happen in an isolated Python_ environment just
for BYCEPS so that its requirements don't clash with different versions
of the same libraries somewhere else in the system.

Python_ already comes with the necessary tools, namely virtualenv_ and
pip_.

With uv_, however, setting up and using a virtual environment (among
other things) became easier and faster.

.. _Python: https://www.python.org/
.. _virtualenv: https://www.virtualenv.org/
.. _pip: https://pip.pypa.io/
.. _uv: https://docs.astral.sh/uv/

This will install BYCEPS' Python dependencies and create a virtual
environment in the process:

.. code-block:: console

    $ cd byceps
    $ uv sync --frozen
