"""
byceps.scripts.util
~~~~~~~~~~~~~~~~~~~

Utilities for scripts

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Callable

from dotenv import load_dotenv

from byceps.application import create_cli_app
from byceps.config.integration import (
    read_configuration_from_file_given_in_env_var,
)


def call_with_app_context(func: Callable) -> None:
    """Call a callable inside of an application context."""
    load_dotenv()
    config = read_configuration_from_file_given_in_env_var()
    app = create_cli_app(config)
    with app.app_context():
        func()
