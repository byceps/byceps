"""
byceps.config.util
~~~~~~~~~~~~~~~~~~

Configuration utilities

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import Counter
from collections.abc import Iterator

from .models import WebAppConfig, WebAppsConfig


def iterate_app_configs(apps_config: WebAppsConfig) -> Iterator[WebAppConfig]:
    """Return all web application configurations contained in this
    applications configuration.
    """
    if apps_config.admin:
        yield apps_config.admin

    if apps_config.api:
        yield apps_config.api

    yield from apps_config.sites


def find_duplicate_server_names(apps_config: WebAppsConfig) -> set[str]:
    """Return server names configured multiple times."""
    server_names = _get_server_names(apps_config)
    counter = Counter(server_names)
    return {server_name for server_name, count in counter.items() if count > 1}


def _get_server_names(apps_config: WebAppsConfig) -> list[str]:
    return [
        app_config.server_name
        for app_config in iterate_app_configs(apps_config)
    ]
