# a party site configuration file to be used in tests

SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
SERVER_NAME = 'www.acmecon.test'
SESSION_COOKIE_SECURE = True
TESTING = True

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps_test:test@127.0.0.1/byceps_test'

REDIS_URL = 'redis://127.0.0.1:6379/0'

APP_MODE = 'site'
SITE_ID = 'acmecon-2014-website'

MAIL_DEBUG = False
MAIL_DEFAULT_SENDER = 'BYCEPS <noreply@example.com>'
MAIL_SUPPRESS_SEND = True

JOBS_ASYNC = False
