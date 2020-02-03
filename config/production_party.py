# an examplary configuration file of a public party web application to
# be run in production

MAX_CONTENT_LENGTH = 4000000
PROPAGATE_EXCEPTIONS = True

# Set a custom secret key for running in production!
# To generate one:
#     $ python -c 'import os; print(os.urandom(24))'
SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

SESSION_COOKIE_SECURE = True

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps:boioioing@127.0.0.1/byceps'

REDIS_URL = 'unix:///var/run/redis/redis.sock?db=0'

SITE_MODE = 'public'
SITE_ID = 'example-prod'
BRAND = 'example-brand'
PARTY = 'example-party-1'

MAIL_DEBUG = False
MAIL_DEFAULT_SENDER = 'BYCEPS <noreply@example.com>'
MAIL_SUPPRESS_SEND = False
