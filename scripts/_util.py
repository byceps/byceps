"""
byceps.scripts.util
~~~~~~~~~~~~~~~~~~~

Utilities for scripts

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager

from byceps.application import create_app


@contextmanager
def app_context(config_filename):
    """Provide a context in which the application is available with the
    specified configuration.
    """
    app = create_app(config_filename)
    with app.app_context():
        yield app
