# Exemplary production configuration

# Enable this if you want a tool like Sentry
# handle exceptions rather than Flask.
PROPAGATE_EXCEPTIONS = False

# Set a custom secret key before running in production!
# To generate one:
#     $ byceps generate-secret-key
#SECRET_KEY = ''

# TODO: Adjust `SQLALCHEMY_DATABASE_URI`!
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://byceps:boioioing@127.0.0.1/byceps'

REDIS_URL = 'redis://127.0.0.1:6379/0'
# Or, if you want to access Redis via unix socket instead:
#REDIS_URL = 'unix:///var/run/redis/redis.sock?db=0'
