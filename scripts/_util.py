"""
byceps.scripts.util
~~~~~~~~~~~~~~~~~~~

Utilities for scripts

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from contextlib import contextmanager

from byceps.application import create_app


@contextmanager
def app_context():
    """Provide a context in which the application is available with the
    specified configuration.
    """
    app = create_app()
    with app.app_context():
        yield app
