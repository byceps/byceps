"""
byceps.config.models
~~~~~~~~~~~~~~~~~~~~

Configuration models

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


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

    def is_metrics(self) -> bool:
        return self == AppMode.metrics

    def is_site(self) -> bool:
        return self == AppMode.site

    def is_worker(self) -> bool:
        return self == AppMode.worker

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}[{self.name}]'


@dataclass(frozen=True, slots=True)
class BycepsConfig:
    locale: str
    propagate_exceptions: bool
    timezone: str
    secret_key: str
    apps: AppsConfig
    database: DatabaseConfig
    debug: DebugConfig
    development: DevelopmentConfig | None
    discord: DiscordConfig | None
    invoiceninja: InvoiceNinjaConfig | None
    jobs: JobsConfig
    metrics: MetricsConfig
    payment_gateways: PaymentGatewaysConfig | None
    redis: RedisConfig
    smtp: SmtpConfig
    styleguide: StyleguideConfig


@dataclass(frozen=True, slots=True)
class AppsConfig:
    admin: AdminAppConfig | None
    api: ApiAppConfig | None
    sites: list[SiteAppConfig]


@dataclass(frozen=True, slots=True)
class _BaseAppConfig:
    server_name: str


@dataclass(frozen=True, slots=True)
class AdminAppConfig(_BaseAppConfig):
    pass


@dataclass(frozen=True, slots=True)
class ApiAppConfig(_BaseAppConfig):
    pass


@dataclass(frozen=True, slots=True)
class SiteAppConfig(_BaseAppConfig):
    site_id: str


AppConfig = AdminAppConfig | ApiAppConfig | SiteAppConfig


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str


@dataclass(frozen=True, slots=True)
class DebugConfig:
    enabled: bool
    toolbar_enabled: bool


@dataclass(frozen=True, slots=True)
class DevelopmentConfig:
    pass


@dataclass(frozen=True, slots=True)
class DiscordConfig:
    enabled: bool
    client_id: str
    client_secret: str


@dataclass(frozen=True, slots=True)
class InvoiceNinjaConfig:
    enabled: bool
    base_url: str
    api_key: str


@dataclass(frozen=True, slots=True)
class JobsConfig:
    asynchronous: bool


@dataclass(frozen=True, slots=True)
class MetricsConfig:
    enabled: bool


@dataclass(frozen=True, slots=True)
class PaymentGatewaysConfig:
    paypal: PaypalConfig | None
    stripe: StripeConfig | None


@dataclass(frozen=True, slots=True)
class PaypalConfig:
    enabled: bool
    client_id: str
    client_secret: str
    environment: str


@dataclass(frozen=True, slots=True)
class RedisConfig:
    url: str


@dataclass(frozen=True, slots=True)
class SmtpConfig:
    host: str
    port: int
    starttls: bool
    use_ssl: bool
    username: str | None
    password: str | None
    suppress_send: bool


@dataclass(frozen=True, slots=True)
class StripeConfig:
    enabled: bool
    secret_key: str
    publishable_key: str
    webhook_secret: str


@dataclass(frozen=True, slots=True)
class StyleguideConfig:
    enabled: bool
