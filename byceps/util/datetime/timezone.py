"""
byceps.util.datetime.timezone
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Timezone helpers

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import current_app


def get_timezone_string() -> str:
    """Return the configured default timezone as a string."""
    return current_app.config['TIMEZONE']
