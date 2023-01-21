*******
Testing
*******

BYCEPS comes with a quite extensive (but not all-encompassing) suite of
tests to be able to verify that at least a big part works as intended.

Running the tests is mostly useful for development of BYCEPS itself as
well as for customization.

.. important:: Before continuing, make sure that the :doc:`virtual
   environment </installation/virtual-env>` is set up and activated.

In the activated virtual environment, first install the test
dependencies:

.. code:: sh

    (venv)$ pip install -r requirements-test.txt

Then run the tests:

.. code:: sh

    (venv)$ pytest

To abort on encountering the first failing test case:

.. code:: sh

    (venv)$ pytest -x
