"""
byceps.config
~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import Any, Optional

from flask import current_app, Flask

from .services.site.transfer.models import SiteID


EXTENSION_KEY = 'byceps_config'
KEY_APP_MODE = 'app_mode'
KEY_SITE_ID = 'site_id'


AppMode = Enum('AppMode', ['public', 'admin'])
AppMode.is_admin = lambda self: self == AppMode.admin
AppMode.is_public = lambda self: self == AppMode.public


class ConfigurationError(Exception):
    pass


def init_app(app: Flask) -> None:
    app.extensions[EXTENSION_KEY] = {}

    app_mode = _determine_app_mode(app)
    set_extension_value(KEY_APP_MODE, app_mode, app)

    if app_mode.is_public():
        site_id = _determine_site_id(app)
        set_extension_value(KEY_SITE_ID, site_id, app)


def get_extension_value(key: str, app: Optional[Flask]=None) -> Any:
    """Return the value for the key in this application's own extension
    namespace.

    It is expected that the value has already been set. An exception is
    raised if that is not the case.
    """
    if app is None:
        app = current_app

    extension = app.extensions[EXTENSION_KEY]
    return extension[key]


def set_extension_value(key: str, value: Any, app: Flask) -> None:
    """Set/replace the value for the key in this application's own
    extension namespace.
    """
    extension = app.extensions[EXTENSION_KEY]
    extension[key] = value


# -------------------------------------------------------------------- #
# app mode


def _determine_app_mode(app: Flask) -> AppMode:
    value = app.config.get('APP_MODE')
    if value is None:
        raise ConfigurationError('No app mode configured.')

    try:
        return AppMode[value]
    except KeyError:
        raise ConfigurationError(f'Invalid app mode "{value}" configured.')


def get_app_mode(app: Optional[Flask]=None) -> AppMode:
    """Return the mode the site should run in."""
    return get_extension_value(KEY_APP_MODE, app)


# -------------------------------------------------------------------- #
# site ID


def _determine_site_id(app: Flask) -> SiteID:
    site_id = app.config.get('SITE_ID')
    if site_id is None:
        raise ConfigurationError('No site ID configured.')

    return site_id


def get_current_site_id(app: Optional[Flask]=None) -> SiteID:
    """Return the id of the current site."""
    return get_extension_value(KEY_SITE_ID, app)
