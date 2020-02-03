# a party site configuration file to be used in tests

from pathlib import Path


SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
SERVER_NAME = 'example.com'
SESSION_COOKIE_SECURE = True
TESTING = True

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps_test:test@127.0.0.1/byceps_test'

REDIS_URL = 'redis://127.0.0.1:6379/0'

SITE_MODE = 'public'
SITE_ID = 'acmecon-2014-website'
BRAND = 'acmecon'
PARTY = 'acmecon-2014'

PATH_DATA = Path('./data')
PATH_GLOBAL = PATH_DATA / 'global'
PATH_BRAND = PATH_DATA / 'brands' / BRAND
PATH_PARTY = PATH_DATA / 'parties' / PARTY

MAIL_DEBUG = False
MAIL_DEFAULT_SENDER = 'BYCEPS <noreply@example.com>'
MAIL_SUPPRESS_SEND = True

JOBS_ASYNC = False
