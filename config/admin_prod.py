# Exemplary production configuration for the admin application

# TODO: Adjust `SECRET_KEY`!
SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
SESSION_COOKIE_SECURE = True

# TODO: Adjust `SQLALCHEMY_DATABASE_URI`!
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps:boioioing@127.0.0.1/byceps'

REDIS_URL = 'redis://127.0.0.1:6379/0'

RQ_DASHBOARD_ENABLED = True

APP_MODE = 'admin'

MAIL_DEBUG = False
MAIL_SUPPRESS_SEND = False

DEBUG_TOOLBAR_ENABLED = False
STYLE_GUIDE_ENABLED = False
