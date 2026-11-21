"""
byceps.config.parser
~~~~~~~~~~~~~~~~~~~~

Configuration parser

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from pathlib import Path

from pydantic import TypeAdapter, ValidationError
import rtoml

from byceps.util.result import Err, Ok, Result

from .models import (
    AdminWebAppConfig,
    ApiWebAppConfig,
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
    SiteWebAppConfig,
    SmtpConfig,
    StripeConfig,
    TomlConfig,
    WebAppsConfig,
)
from .util import find_duplicate_server_names, iterate_app_configs


type ParsingResult[T] = Result[T, list[str]]


def _validate_apps_config(
    web_apps_config: WebAppsConfig,
) -> ParsingResult[None]:
    app_configs = list(iterate_app_configs(web_apps_config))
    if not app_configs:
        return Err(['No applications configured'])

    duplicate_server_names = find_duplicate_server_names(web_apps_config)
    if duplicate_server_names:
        server_names_str = ', '.join(sorted(duplicate_server_names))
        return Err([f'Non-unique server names configured: {server_names_str}'])

    return Ok(None)


def parse_config(
    toml: str,
) -> ParsingResult[tuple[BycepsConfig, WebAppsConfig]]:
    """Parse configuration in TOML format."""
    match _parse_toml_config(toml):
        case Ok(toml_config):
            pass
        case Err(e):
            return Err(e)

    data_path = Path('./data')
    testing = False

    byceps_config = BycepsConfig(
        data_path=data_path,
        locale=toml_config.locale,
        propagate_exceptions=toml_config.propagate_exceptions,
        secret_key=toml_config.secret_key,
        testing=testing,
        timezone=toml_config.timezone,
        database=toml_config.database,
        development=toml_config.development,
        discord=toml_config.discord,
        invoiceninja=toml_config.invoiceninja,
        jobs=toml_config.jobs,
        metrics=toml_config.metrics,
        payment_gateways=toml_config.payment_gateways,
        redis=toml_config.redis,
        smtp=toml_config.smtp,
    )

    web_apps_config = toml_config.apps

    return Ok((byceps_config, web_apps_config))


toml_config_adapter = TypeAdapter(TomlConfig)


def _parse_toml_config(toml: str) -> ParsingResult[TomlConfig]:
    data = rtoml.loads(toml)

    try:
        toml_config = toml_config_adapter.validate_python(data)
    except ValidationError as e:
        errors: list[str] = []

        for error in e.errors(
            include_context=False, include_input=False, include_url=False
        ):
            field_name = '.'.join(error['loc'])
            msg = error['msg']
            errors.append(f'{field_name}: {msg}')

        return Err(errors)

    match _validate_apps_config(toml_config.apps):
        case Err(e):
            return Err(e)

    return Ok(toml_config)
