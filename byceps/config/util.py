"""
byceps.config.util
~~~~~~~~~~~~~~~~~~

Configuration utilities

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator

from .models import AppConfig, AppsConfig


def iterate_app_configs(apps_config: AppsConfig) -> Iterator[AppConfig]:
    """Return all application configurations contained in this
    applications configuration.
    """
    if apps_config.admin:
        yield apps_config.admin

    if apps_config.api:
        yield apps_config.api

    yield from apps_config.sites


def find_conflicting_server_names(apps_config: AppsConfig) -> set[str]:
    """Return server names configured multiple times."""
    defined_server_names = set()
    conflicting_server_names = set()

    for server_name in _get_server_names(apps_config):
        if server_name in defined_server_names:
            conflicting_server_names.add(server_name)
        else:
            defined_server_names.add(server_name)

    return conflicting_server_names


def _get_server_names(apps_config: AppsConfig) -> list[str]:
    return [
        app_config.server_name
        for app_config in iterate_app_configs(apps_config)
    ]
