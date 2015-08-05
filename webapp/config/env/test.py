from datetime import timedelta
from pathlib import Path


DEBUG = False
PERMANENT_SESSION_LIFETIME = timedelta(14)
SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
SERVER_NAME = 'example.com'
SESSION_COOKIE_SECURE = True
TESTING = True

LOCALE = 'de_DE.UTF-8'
LOCALES_FORMS = ['de']

SQLALCHEMY_DATABASE_URI = 'postgresql+pg8000://byceps_test:test@127.0.0.1/byceps_test'
SQLALCHEMY_ECHO = False

REDIS_URL = 'redis://127.0.0.1:6379/0'

MODE = 'public'
PARTY = 'acme-2014'

PATH_DATA = Path('./data')
PATH_USER_AVATAR_IMAGES = PATH_DATA / 'users/avatars'

BOARD_TOPICS_PER_PAGE = 10
BOARD_POSTINGS_PER_PAGE = 10

MAIL_DEBUG = False
MAIL_DEFAULT_SENDER = 'BYCEPS <noreply@example.com>'
MAIL_SUPPRESS_SEND = True

JOBS_ASYNC = False
