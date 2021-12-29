# Exemplary production configuration for a public site

# Enable this if you want a tool like Sentry
# handle exceptions rather than Flask.
PROPAGATE_EXCEPTIONS = False

# Set a custom secret key for running in production!
# To generate one:
#     $ python -c 'import os; print(os.urandom(24))'
SECRET_KEY = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

SESSION_COOKIE_SECURE = True

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps:boioioing@127.0.0.1/byceps'

REDIS_URL = 'unix:///var/run/redis/redis.sock?db=0'

APP_MODE = 'site'
SITE_ID = 'example-site'

MAIL_DEBUG = False
MAIL_SUPPRESS_SEND = False
