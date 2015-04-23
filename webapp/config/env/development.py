from datetime import timedelta
from pathlib import Path


DEBUG = True
PERMANENT_SESSION_LIFETIME = timedelta(14)
SECRET_KEY = b'\xcb;\xcd\xdc\x11\xf2\xa8\x08_Ks\xa3\xb0\xc5K/\x9b\xf1\xd9\xdc_\x16\x8e\xa8'
SESSION_COOKIE_SECURE = True

LOCALE = 'de_DE.UTF-8'
LOCALES_FORMS = ['de']

SQLALCHEMY_DATABASE_URI = 'postgresql+pg8000://byceps:boioioing@127.0.0.1/byceps'
SQLALCHEMY_ECHO = False

REDIS_URL = 'redis://127.0.0.1:6379/0'

MODE = 'public'
PARTY = 'lanresort-2014'

PATH_DATA = Path('./data')
PATH_CONTENT = PATH_DATA / 'party_content' / PARTY
PATH_USER_AVATAR_IMAGES = PATH_DATA / 'users/avatars'

BOARD_TOPICS_PER_PAGE = 10
BOARD_POSTINGS_PER_PAGE = 10

MAIL_DEBUG = True
MAIL_DEFAULT_SENDER = 'LANresort <noreply@lanresort.de>'
MAIL_SUPPRESS_SEND = True
