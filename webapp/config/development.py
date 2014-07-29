from datetime import timedelta
from pathlib import Path


DEBUG = True
PERMANENT_SESSION_LIFETIME = timedelta(14)
SECRET_KEY = b'\xcb;\xcd\xdc\x11\xf2\xa8\x08_Ks\xa3\xb0\xc5K/\x9b\xf1\xd9\xdc_\x16\x8e\xa8'

LOCALE = 'de_DE.UTF-8'

SQLALCHEMY_DATABASE_URI = 'postgresql+pg8000://byceps:boioioing@127.0.0.1/byceps'
SQLALCHEMY_ECHO = False

PATH_USER_IMAGES = Path('./data/user/avatars')
