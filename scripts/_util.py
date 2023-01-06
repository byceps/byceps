"""
byceps.scripts.util
~~~~~~~~~~~~~~~~~~~

Utilities for scripts

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from contextlib import contextmanager
from typing import Callable

from byceps.application import create_app


@contextmanager
def app_context():
    """Provide a context in which the application is available with the
    specified configuration.
    """
    app = create_app()
    with app.app_context():
        yield app


def call_with_app_context(func: Callable) -> None:
    """Call a callable inside of an application context."""
    with app_context():
        func()
