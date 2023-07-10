"""
byceps.config
~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from enum import Enum

from flask import Flask


class AppMode(Enum):
    admin = object()
    base = object()
    cli = object()
    site = object()
    worker = object()

    def is_admin(self) -> bool:
        return self == AppMode.admin

    def is_base(self) -> bool:
        return self == AppMode.base

    def is_cli(self) -> bool:
        return self == AppMode.cli

    def is_site(self) -> bool:
        return self == AppMode.site

    def is_worker(self) -> bool:
        return self == AppMode.worker


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
