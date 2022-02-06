Set Up a Virtual Python Environment
===================================

The installation should happen in an isolated Python_ environment just
for BYCEPS so that its requirements don't clash with different versions
of the same libraries somewhere else in the system.

Python_ already comes with the necessary tools, namely virtualenv_ and
pip_.

.. _Python: https://www.python.org/
.. _virtualenv: https://www.virtualenv.org/
.. _pip: https://www.pip-installer.org/

Change into the BYCEPS path and create a virtual environment (named
"venv") there:

.. code-block:: sh

    $ cd byceps
    $ python3 -m venv venv

Activate it (but don't change into its path):

.. code-block:: sh

    $ . ./venv/bin/activate

Note that the first dot is the `dot command`_, followed by a relative
file name (which is written as explicitly relative to the current path,
``./``).

Whenever you want to activate the virtual environment, make sure to do
that either in the path in which you have created it using the above
command, or adjust the path to reference it relatively (e.g.
``../../venv/bin/activate``) or absolutely (e.g.
``/var/www/byceps/venv/bin/activate``).

Make sure the correct version of Python is used:

.. code-block:: sh

    (venv)$ python -V
    Python 3.9.2

It's probably a good idea to update pip_ to the current version:

.. code-block:: sh

    (venv)$ pip install --upgrade pip

Install the Python depdendencies via pip_:

.. code-block:: sh

    (venv)$ pip install -r requirements.txt

Install BYCEPS in editable mode to make the ``byceps`` command as well
as the package of the same name available:

.. code-block:: sh

    (venv)$ pip install -e .

.. _dot command: https://en.wikipedia.org/wiki/Dot_(Unix)
