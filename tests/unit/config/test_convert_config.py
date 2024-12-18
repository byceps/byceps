"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.config.converter import convert_config
from byceps.config.models import (
    AppsConfig,
    BycepsConfig,
    DatabaseConfig,
    DebugConfig,
    JobsConfig,
    MetricsConfig,
    RedisConfig,
    SmtpConfig,
    StyleguideConfig,
)


def test_convert_config():
    expected = {
        'BABEL_DEFAULT_TIMEZONE': 'Europe/Berlin',
        'DEBUG': True,
        'DEBUG_TOOLBAR_ENABLED': True,
        'JOBS_ASYNC': True,
        'LOCALE': 'de',
        'MAIL_HOST': 'localhost',
        'MAIL_PASSWORD': 'smtppass',
        'MAIL_PORT': 25,
        'MAIL_STARTTLS': True,
        'MAIL_SUPPRESS_SEND': False,
        'MAIL_USE_SSL': False,
        'MAIL_USERNAME': 'smtpuser',
        'METRICS_ENABLED': True,
        'PROPAGATE_EXCEPTIONS': True,
        'REDIS_URL': 'redis://127.0.0.1:6379/0',
        'SECRET_KEY': '<RANDOM-BYTES>',
        'SHOP_ORDER_EXPORT_TIMEZONE': 'Europe/Berlin',
        'SQLALCHEMY_DATABASE_URI': 'postgresql+psycopg://dbuser:dbpass@127.0.0.1:5432/db',
        'STYLE_GUIDE_ENABLED': True,
        'TIMEZONE': 'Europe/Berlin',
    }

    config = BycepsConfig(
        locale='de',
        propagate_exceptions=True,
        secret_key='<RANDOM-BYTES>',
        timezone='Europe/Berlin',
        apps=AppsConfig(
            admin=None,
            api=None,
            sites=[],
        ),
        database=DatabaseConfig(
            host='127.0.0.1',
            port=5432,
            username='dbuser',
            password='dbpass',
            database='db',
        ),
        debug=DebugConfig(
            enabled=True,
            toolbar_enabled=True,
        ),
        discord=None,
        jobs=JobsConfig(
            asynchronous=True,
        ),
        metrics=MetricsConfig(
            enabled=True,
        ),
        payment_gateways={},
        redis=RedisConfig(
            url='redis://127.0.0.1:6379/0',
        ),
        smtp=SmtpConfig(
            host='localhost',
            port=25,
            starttls=True,
            use_ssl=False,
            username='smtpuser',
            password='smtppass',
            suppress_send=False,
        ),
        styleguide=StyleguideConfig(
            enabled=True,
        ),
    )

    actual = convert_config(config)

    assert actual == expected
