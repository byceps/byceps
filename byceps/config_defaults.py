"""
byceps.config_defaults
~~~~~~~~~~~~~~~~~~~~~~

Default configuration values

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import timedelta
from pathlib import Path


# database connection
SQLALCHEMY_ECHO = False

# Avoid connection errors after database becomes temporarily
# unreachable, then becomes reachable again.
SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}

# Disable Flask-SQLAlchemy's tracking of object modifications.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# job queue
JOBS_ASYNC = True

# REST API
API_ENABLED = True

# metrics
METRICS_ENABLED = False

# RQ dashboard (for job queue)
RQ_DASHBOARD_POLL_INTERVAL = 2500
RQ_DASHBOARD_WEB_BACKGROUND = 'white'

# login sessions
PERMANENT_SESSION_LIFETIME = timedelta(14)
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True

# localization
LOCALE = 'de_DE.UTF-8'
LOCALES_FORMS = ['de']
TIMEZONE = 'Europe/Berlin'
BABEL_DEFAULT_LOCALE = LOCALE
BABEL_DEFAULT_TIMEZONE = TIMEZONE

# static content files path
PATH_DATA = Path('./data')

# Limit incoming request content.
MAX_CONTENT_LENGTH = 4000000

# e-mail
MAIL_DEFAULT_SENDER = 'BYCEPS <noreply@byceps.example>'

# shop
SHOP_ORDER_EXPORT_TIMEZONE = 'Europe/Berlin'
