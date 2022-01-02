# Exemplary development configuration

import os


DEBUG = True

SECRET_KEY = 'secret-key-for-development'
SESSION_COOKIE_SECURE = False

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps:boioioing@127.0.0.1/byceps'

REDIS_URL = 'redis://127.0.0.1:6379/0'

APP_MODE = os.environ.get('APP_MODE')
SITE_ID = os.environ.get('SITE_ID')

MAIL_TRANSPORT = 'logging'

DEBUG_TOOLBAR_ENABLED = True
STYLE_GUIDE_ENABLED = True
