# Exemplary development configuration for a public site

SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
SESSION_COOKIE_SECURE = True

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps:boioioing@127.0.0.1/byceps'

REDIS_URL = 'redis://127.0.0.1:6379/0'

APP_MODE = 'site'
SITE_ID = 'example-site'

MAIL_DEBUG = True
MAIL_DEFAULT_SENDER = 'BYCEPS <noreply@site.example>'
MAIL_SUPPRESS_SEND = True
