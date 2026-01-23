"""
byceps.config.models
~~~~~~~~~~~~~~~~~~~~

Configuration models

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from byceps.services.site.models import SiteID


class AppMode(Enum):
    admin = object()
    api = object()
    cli = object()
    metrics = object()
    site = object()
    worker = object()

    def is_admin(self) -> bool:
        return self == AppMode.admin

    def is_api(self) -> bool:
        return self == AppMode.api

    def is_cli(self) -> bool:
        return self == AppMode.cli

    def is_site(self) -> bool:
        return self == AppMode.site

    def is_worker(self) -> bool:
        return self == AppMode.worker

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}[{self.name}]'


@dataclass(frozen=True, kw_only=True, slots=True)
class BycepsConfig:
    data_path: Path
    locale: str
    propagate_exceptions: bool | None
    testing: bool
    timezone: str
    secret_key: str
    database: DatabaseConfig
    development: DevelopmentConfig
    discord: DiscordConfig | None
    invoiceninja: InvoiceNinjaConfig | None
    jobs: JobsConfig
    metrics: MetricsConfig
    payment_gateways: PaymentGatewaysConfig | None
    redis: RedisConfig
    smtp: SmtpConfig


@dataclass(frozen=True, kw_only=True, slots=True)
class AppsConfig:
    admin: AdminWebAppConfig | None
    api: ApiAppConfig | None
    sites: list[SiteAppConfig]


@dataclass(frozen=True, kw_only=True, slots=True)
class AppConfig:
    pass


@dataclass(frozen=True, kw_only=True, slots=True)
class WebAppConfig(AppConfig):
    server_name: str


@dataclass(frozen=True, kw_only=True, slots=True)
class AdminWebAppConfig(WebAppConfig):
    pass


@dataclass(frozen=True, kw_only=True, slots=True)
class ApiAppConfig(WebAppConfig):
    pass


@dataclass(frozen=True, kw_only=True, slots=True)
class CliAppConfig(AppConfig):
    pass


@dataclass(frozen=True, kw_only=True, slots=True)
class SiteAppConfig(WebAppConfig):
    site_id: SiteID


@dataclass(frozen=True, kw_only=True, slots=True)
class WorkerAppConfig(AppConfig):
    pass


@dataclass(frozen=True, kw_only=True, slots=True)
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str


@dataclass(frozen=True, kw_only=True, slots=True)
class DevelopmentConfig:
    style_guide_enabled: bool
    toolbar_enabled: bool


@dataclass(frozen=True, kw_only=True, slots=True)
class DiscordConfig:
    enabled: bool
    client_id: str
    client_secret: str


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceNinjaConfig:
    enabled: bool
    base_url: str
    api_key: str


@dataclass(frozen=True, kw_only=True, slots=True)
class JobsConfig:
    asynchronous: bool


@dataclass(frozen=True, kw_only=True, slots=True)
class MetricsConfig:
    enabled: bool


@dataclass(frozen=True, kw_only=True, slots=True)
class PaymentGatewaysConfig:
    paypal: PaypalConfig | None
    stripe: StripeConfig | None


@dataclass(frozen=True, kw_only=True, slots=True)
class PaypalConfig:
    enabled: bool
    client_id: str
    client_secret: str
    environment: str


@dataclass(frozen=True, kw_only=True, slots=True)
class RedisConfig:
    url: str


@dataclass(frozen=True, kw_only=True, slots=True)
class SmtpConfig:
    host: str
    port: int
    starttls: bool
    use_ssl: bool
    username: str | None
    password: str | None
    suppress_send: bool


@dataclass(frozen=True, kw_only=True, slots=True)
class StripeConfig:
    enabled: bool
    secret_key: str
    publishable_key: str
    webhook_secret: str
