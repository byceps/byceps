# an examplary configuration file of a public party web application to
# be run during development

from pathlib import Path


SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
SESSION_COOKIE_SECURE = True

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps:boioioing@127.0.0.1/byceps'

REDIS_URL = 'redis://127.0.0.1:6379/0'

SITE_MODE = 'public'
SITE_ID = 'example-dev'
BRAND = 'example-brand'
PARTY = 'example-party-1'

PATH_DATA = Path('./data')
PATH_BRAND = PATH_DATA / 'brands' / BRAND
PATH_PARTY = PATH_DATA / 'parties' / PARTY

MAIL_DEBUG = True
MAIL_DEFAULT_SENDER = 'BYCEPS <noreply@example.com>'
MAIL_SUPPRESS_SEND = True
