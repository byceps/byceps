"""
byceps.config.models
~~~~~~~~~~~~~~~~~~~~

Configuration models

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BycepsConfig:
    locale: str
    propagate_exceptions: bool
    timezone: str
    secret_key: str
    database: DatabaseConfig
    debug: DebugConfig
    discord: DiscordConfig | None
    jobs: JobsConfig
    metrics: MetricsConfig
    paypal: PaypalConfig | None
    redis: RedisConfig
    smtp: SmtpConfig
    stripe: StripeConfig | None
    styleguide: StyleguideConfig


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
class DiscordConfig:
    enabled: bool
    client_id: str
    client_secret: str


@dataclass(frozen=True, slots=True)
class JobsConfig:
    asynchronous: bool


@dataclass(frozen=True, slots=True)
class MetricsConfig:
    enabled: bool


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
