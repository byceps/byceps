# a configuration file to be used in tests

SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
SESSION_COOKIE_SECURE = True
TESTING = True

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps_test:test@127.0.0.1/byceps_test'

REDIS_URL = 'redis://127.0.0.1:6379/0'

MAIL_SUPPRESS_SEND = True

JOBS_ASYNC = False
