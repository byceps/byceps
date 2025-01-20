*******
Testing
*******

BYCEPS comes with a quite extensive (but not all-encompassing) suite of
tests to be able to verify that at least a big part works as intended.

Running the tests is mostly useful for development of BYCEPS itself as
well as for customization.

First, install the test dependencies:

.. code:: console

    $ uv sync --group test

Then run the tests:

.. code:: console

    $ uv run pytest

To abort on encountering the first failing test case:

.. code:: console

    $ uv run pytest -x
