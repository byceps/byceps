"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.config.parser import parse_config
from byceps.config.models import (
    BycepsConfig,
    DatabaseConfig,
    DebugConfig,
    DiscordConfig,
    JobsConfig,
    MetricsConfig,
    PaypalConfig,
    RedisConfig,
    SmtpConfig,
    StripeConfig,
    StyleguideConfig,
)
from byceps.util.result import Err, Ok


def test_parse_config():
    expected = Ok(
        BycepsConfig(
            locale='de',
            propagate_exceptions=True,
            secret_key='<RANDOM-BYTES>',
            timezone='Europe/Berlin',
            database=DatabaseConfig(
                host='db-host',
                port=54321,
                username='db-user',
                password='db-password',
                database='db-database',
            ),
            debug=DebugConfig(
                enabled=True,
                toolbar_enabled=True,
            ),
            discord=DiscordConfig(
                client_id='discord-client-id',
                client_secret='discord-client-secret',
            ),
            jobs=JobsConfig(
                asynchronous=False,
            ),
            metrics=MetricsConfig(
                enabled=True,
            ),
            paypal=PaypalConfig(
                client_id='paypal-client-id',
                client_secret='paypal-client-secret',
                environment='sandbox',
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
            stripe=StripeConfig(
                secret_key='stripe-secret-key',
                publishable_key='stripe-publishable-key',
                webhook_secret='stripe-webhook-secret',
            ),
            styleguide=StyleguideConfig(
                enabled=True,
            ),
        )
    )

    toml = """\
    locale = "de"
    propagate_exceptions = true
    secret_key = "<RANDOM-BYTES>"
    timezone = "Europe/Berlin"

    [database]
    host = "db-host"
    port = 54321
    username = "db-user"
    password = "db-password"
    database = "db-database"

    [debug]
    enabled = true
    toolbar_enabled = true

    [discord]
    client_id = "discord-client-id"
    client_secret = "discord-client-secret"

    [jobs]
    async = false

    [metrics]
    enabled = true

    [paypal]
    client_id = "paypal-client-id"
    client_secret = "paypal-client-secret"
    environment = "sandbox"

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

    [stripe]
    secret_key = "stripe-secret-key"
    publishable_key = "stripe-publishable-key"
    webhook_secret = "stripe-webhook-secret"

    [styleguide]
    enabled = true
    """

    assert parse_config(toml) == expected


def test_parse_config_defaults():
    expected = Ok(
        BycepsConfig(
            locale='en',
            propagate_exceptions=False,
            secret_key='<RANDOM-BYTES>',
            timezone='Europe/London',
            database=DatabaseConfig(
                host='localhost',
                port=5432,
                username='db-user',
                password='db-password',
                database='db-database',
            ),
            debug=DebugConfig(
                enabled=False,
                toolbar_enabled=False,
            ),
            discord=DiscordConfig(
                enabled=False,
                client_id='',
                client_secret='',
            ),
            metrics=MetricsConfig(
                enabled=False,
            ),
            jobs=JobsConfig(
                asynchronous=True,
            ),
            paypal=PaypalConfig(
                enabled=False,
                client_id='',
                client_secret='',
                environment='',
            ),
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
            stripe=StripeConfig(
                enabled=False,
                secret_key='',
                publishable_key='',
                webhook_secret='',
            ),
            styleguide=StyleguideConfig(
                enabled=False,
            ),
        )
    )

    toml = """\
    secret_key = "<RANDOM-BYTES>"
    timezone = "Europe/London"

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
            'Key "secret_key" missing',
            'Key "timezone" missing',
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
