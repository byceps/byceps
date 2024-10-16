"""
byceps.config_defaults
~~~~~~~~~~~~~~~~~~~~~~

Default configuration values

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import timedelta
from pathlib import Path


# metrics
METRICS_ENABLED = False

# login sessions
PERMANENT_SESSION_LIFETIME = timedelta(14)
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True

# localization
LOCALE = 'de'
LOCALES_FORMS = ['de']
TIMEZONE = 'Europe/Berlin'
BABEL_DEFAULT_LOCALE = LOCALE
BABEL_DEFAULT_TIMEZONE = TIMEZONE

# static content files path
PATH_DATA = Path('./data')

# Limit incoming request content.
MAX_CONTENT_LENGTH = 4000000

# shop
SHOP_ORDER_EXPORT_TIMEZONE = 'Europe/Berlin'
