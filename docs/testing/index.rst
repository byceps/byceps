*******
Testing
*******

BYCEPS comes with a quite extensive (but not all-encompassing) suite of
tests to be able to verify that at least a big part works as intended.

Running the tests is mostly useful for development of BYCEPS itself as
well as for customization.

First, install the test dependencies:

.. code-block:: console

    $ uv sync --frozen --group test

Then run the tests:

.. code-block:: console

    $ uv run pytest

To abort on encountering the first failing test case:

.. code-block:: console

    $ uv run pytest -x
