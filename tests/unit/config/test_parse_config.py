"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

from byceps.config.parser import parse_config
from byceps.config.models import (
    AdminAppConfig,
    ApiAppConfig,
    AppsConfig,
    BycepsConfig,
    DatabaseConfig,
    DevelopmentConfig,
    DiscordConfig,
    InvoiceNinjaConfig,
    JobsConfig,
    MetricsConfig,
    PaymentGatewaysConfig,
    PaypalConfig,
    RedisConfig,
    SiteAppConfig,
    SmtpConfig,
    StripeConfig,
)
from byceps.util.result import Err, Ok


def test_parse_config():
    expected = Ok(
        BycepsConfig(
            data_path=Path('./data'),
            locale='de',
            propagate_exceptions=True,
            secret_key='<RANDOM-BYTES>',
            testing=False,
            timezone='Europe/Berlin',
            apps=AppsConfig(
                admin=AdminAppConfig(
                    server_name='admin.test',
                ),
                api=ApiAppConfig(
                    server_name='api.test',
                ),
                sites=[
                    SiteAppConfig(
                        server_name='site1.test',
                        site_id='site1',
                    ),
                    SiteAppConfig(
                        server_name='site2.test',
                        site_id='site2',
                    ),
                ],
            ),
            database=DatabaseConfig(
                host='db-host',
                port=54321,
                username='db-user',
                password='db-password',
                database='db-database',
            ),
            development=DevelopmentConfig(
                style_guide_enabled=True,
                toolbar_enabled=True,
            ),
            discord=DiscordConfig(
                enabled=True,
                client_id='discord-client-id',
                client_secret='discord-client-secret',
            ),
            invoiceninja=InvoiceNinjaConfig(
                enabled=True,
                base_url='https://invoiceninja.example',
                api_key='invoiceninja-api-key',
            ),
            jobs=JobsConfig(
                asynchronous=False,
            ),
            metrics=MetricsConfig(
                enabled=True,
            ),
            payment_gateways=PaymentGatewaysConfig(
                paypal=PaypalConfig(
                    enabled=True,
                    client_id='paypal-client-id',
                    client_secret='paypal-client-secret',
                    environment='sandbox',
                ),
                stripe=StripeConfig(
                    enabled=True,
                    secret_key='stripe-secret-key',
                    publishable_key='stripe-publishable-key',
                    webhook_secret='stripe-webhook-secret',
                ),
            ),
            redis=RedisConfig(
                url='redis://127.0.0.1:6379/0',
            ),
            smtp=SmtpConfig(
                host='smtp-host',
                port=2525,
                starttls=True,
                use_ssl=True,
                username='smtp-user',
                password='smtp-password',
                suppress_send=True,
            ),
        )
    )

    toml = """\
    locale = "de"
    propagate_exceptions = true
    secret_key = "<RANDOM-BYTES>"
    timezone = "Europe/Berlin"

    [apps]
    admin = { server_name = "admin.test" }
    api = { server_name = "api.test" }
    sites = [
      { server_name = "site1.test", site_id = "site1" },
      { server_name = "site2.test", site_id = "site2" },
    ]

    [database]
    host = "db-host"
    port = 54321
    username = "db-user"
    password = "db-password"
    database = "db-database"

    [development]
    style_guide_enabled = true
    toolbar_enabled = true

    [discord]
    enabled = true
    client_id = "discord-client-id"
    client_secret = "discord-client-secret"

    [invoiceninja]
    enabled = true
    base_url = "https://invoiceninja.example"
    api_key = "invoiceninja-api-key"

    [jobs]
    asynchronous = false

    [metrics]
    enabled = true

    [payment_gateways.paypal]
    enabled = true
    client_id = "paypal-client-id"
    client_secret = "paypal-client-secret"
    environment = "sandbox"

    [payment_gateways.stripe]
    enabled = true
    secret_key = "stripe-secret-key"
    publishable_key = "stripe-publishable-key"
    webhook_secret = "stripe-webhook-secret"

    [redis]
    url = "redis://127.0.0.1:6379/0"

    [smtp]
    host = "smtp-host"
    port = 2525
    starttls = true
    use_ssl = true
    username = "smtp-user"
    password = "smtp-password"
    suppress_send = true
    """

    assert parse_config(toml) == expected


def test_parse_config_defaults():
    expected = Ok(
        BycepsConfig(
            data_path=Path('./data'),
            locale='en',
            propagate_exceptions=None,
            secret_key='<RANDOM-BYTES>',
            testing=False,
            timezone='Europe/London',
            apps=AppsConfig(
                admin=AdminAppConfig(
                    server_name='admin.test',
                ),
                api=None,
                sites=[],
            ),
            database=DatabaseConfig(
                host='localhost',
                port=5432,
                username='db-user',
                password='db-password',
                database='db-database',
            ),
            development=DevelopmentConfig(
                style_guide_enabled=False,
                toolbar_enabled=False,
            ),
            discord=None,
            invoiceninja=None,
            jobs=JobsConfig(
                asynchronous=True,
            ),
            metrics=MetricsConfig(
                enabled=False,
            ),
            payment_gateways=None,
            redis=RedisConfig(
                url='redis://127.0.0.1:6379/0',
            ),
            smtp=SmtpConfig(
                host='localhost',
                port=25,
                starttls=False,
                use_ssl=False,
                username='',
                password='',
                suppress_send=False,
            ),
        )
    )

    toml = """\
    locale = "en"
    secret_key = "<RANDOM-BYTES>"
    timezone = "Europe/London"

    [apps]
    admin = { server_name = "admin.test" }

    [database]
    username = "db-user"
    password = "db-password"
    database = "db-database"

    [redis]
    url = "redis://127.0.0.1:6379/0"

    [smtp]
    """

    assert parse_config(toml) == expected


def test_parse_incomplete_config():
    expected = Err(
        [
            'Key "locale" missing',
            'Key "secret_key" missing',
            'Key "timezone" missing',
            'Section "apps" missing',
            'Key "username" missing in section "database"',
            'Key "password" missing in section "database"',
            'Section "redis" missing',
            'Section "smtp" missing',
        ]
    )

    toml = """\
    [database]
    host = "db-host"
    port = 54321
    database = "db-database"
    """

    assert parse_config(toml) == expected


def test_parse_config_without_apps():
    expected = Err(
        [
            'No applications configured',
        ]
    )

    toml = """\
    locale = "en"
    secret_key = "<RANDOM-BYTES>"
    timezone = "Europe/London"

    [apps]

    [database]
    username = "db-user"
    password = "db-password"
    database = "db-database"

    [redis]
    url = "redis://127.0.0.1:6379/0"

    [smtp]
    """

    assert parse_config(toml) == expected


def test_parse_config_with_conflicting_server_names():
    expected = Err(
        [
            'Non-unique server names configured: name1.test',
        ]
    )

    toml = """\
    locale = "en"
    secret_key = "<RANDOM-BYTES>"
    timezone = "Europe/London"

    [apps]
    admin = { server_name = "name1.test" }
    api = { server_name = "api.test" }
    sites = [
      { server_name = "name1.test", site_id = "site1" },
      { server_name = "site2.test", site_id = "site2" },
    ]

    [database]
    username = "db-user"
    password = "db-password"
    database = "db-database"

    [redis]
    url = "redis://127.0.0.1:6379/0"

    [smtp]
    """

    assert parse_config(toml) == expected


def test_parse_config_with_conflicting_site_server_names():
    expected = Err(
        [
            'Non-unique server names configured: site1.test',
        ]
    )

    toml = """\
    locale = "en"
    secret_key = "<RANDOM-BYTES>"
    timezone = "Europe/London"

    [apps]
    sites = [
      { server_name = "site1.test", site_id = "site1" },
      { server_name = "site1.test", site_id = "site2" },
    ]

    [database]
    username = "db-user"
    password = "db-password"
    database = "db-database"

    [redis]
    url = "redis://127.0.0.1:6379/0"

    [smtp]
    """

    assert parse_config(toml) == expected
