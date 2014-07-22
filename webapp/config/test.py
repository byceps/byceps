from datetime import timedelta


DEBUG = False
PERMANENT_SESSION_LIFETIME = timedelta(14)
SECRET_KEY = b'\xcb;\xcd\xdc\x11\xf2\xa8\x08_Ks\xa3\xb0\xc5K/\x9b\xf1\xd9\xdc_\x16\x8e\xa8'
TESTING = True

LOCALE = 'de_DE.UTF-8'

SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_ECHO = False
