"""
byceps.config
~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from enum import Enum
import json
import os

from flask import Flask


class AppMode(Enum):
    admin = object()
    api = object()
    base = object()
    cli = object()
    metrics = object()
    site = object()
    worker = object()

    def is_admin(self) -> bool:
        return self == AppMode.admin

    def is_api(self) -> bool:
        return self == AppMode.api

    def is_base(self) -> bool:
        return self == AppMode.base

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


class ConfigurationError(Exception):
    pass


def init_app(app: Flask) -> None:
    app.byceps_app_mode = _determine_app_mode(app)

    if app.byceps_app_mode.is_site():
        if not app.config.get('SITE_ID'):
            raise ConfigurationError('No site ID configured.')


def _determine_app_mode(app: Flask) -> AppMode:
    value = app.config.get('APP_MODE', 'base')

    try:
        return AppMode[value]
    except KeyError as exc:
        raise ConfigurationError(
            f'Invalid app mode "{value}" configured.'
        ) from exc


def parse_value_from_environment(
    key: str,
) -> bool | dict | float | int | list | str | None:
    value = os.environ.get(key)
    if value is None:
        return None

    try:
        # Detect booleans, numbers, collections, `null`/`None`.
        return json.loads(value)
    except Exception:
        # Leave it as a string.
        return value
