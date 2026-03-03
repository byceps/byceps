"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

from byceps.config.converter import convert_config
from byceps.config.models import (
    BycepsConfig,
    DatabaseConfig,
    DevelopmentConfig,
    InvoiceNinjaConfig,
    JobsConfig,
    MetricsConfig,
    PaymentGatewaysConfig,
    RedisConfig,
    SmtpConfig,
)


def test_convert_config():
    expected = {
        'LOCALE': 'de',
        'PROPAGATE_EXCEPTIONS': True,
        'REDIS_URL': 'redis://127.0.0.1:6379/0',
        'SECRET_KEY': '<RANDOM-BYTES>',
        'SHOP_ORDER_EXPORT_TIMEZONE': 'Europe/Berlin',
        'SQLALCHEMY_DATABASE_URI': 'postgresql+psycopg://dbuser:dbpass@127.0.0.1:5432/db',
        'TESTING': True,
        'TIMEZONE': 'Europe/Berlin',
    }

    config = BycepsConfig(
        data_path=Path('./data'),
        locale='de',
        propagate_exceptions=True,
        secret_key='<RANDOM-BYTES>',
        testing=True,
        timezone='Europe/Berlin',
        database=DatabaseConfig(
            host='127.0.0.1',
            port=5432,
            username='dbuser',
            password='dbpass',
            database='db',
        ),
        development=DevelopmentConfig(
            style_guide_enabled=True,
            toolbar_enabled=True,
        ),
        discord=None,
        invoiceninja=InvoiceNinjaConfig(
            enabled=True,
            base_url='https://invoiceninja.example',
            api_key='invoiceninja-api-key',
        ),
        jobs=JobsConfig(
            asynchronous=True,
        ),
        metrics=MetricsConfig(
            enabled=True,
        ),
        payment_gateways=PaymentGatewaysConfig(
            paypal=None,
            stripe=None,
        ),
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
    )

    actual = convert_config(config)

    assert actual == expected
