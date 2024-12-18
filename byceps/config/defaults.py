"""
byceps.config.defaults
~~~~~~~~~~~~~~~~~~~~~~

Default configuration values

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import timedelta
from pathlib import Path


# login sessions
PERMANENT_SESSION_LIFETIME = timedelta(14)
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True

# static content files path
PATH_DATA = Path('./data')

# Limit incoming request content.
MAX_CONTENT_LENGTH = 4000000
