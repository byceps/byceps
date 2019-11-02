"""
byceps.config
~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum

from flask import current_app


STATIC_URL_PREFIX_GLOBAL = '/global'
STATIC_URL_PREFIX_BRAND = '/brand'
STATIC_URL_PREFIX_PARTY = '/party'
STATIC_URL_PREFIX_SITE = '/site'

EXTENSION_KEY = 'byceps_config'
KEY_SITE_MODE = 'site_mode'
KEY_SITE_ID = 'site_id'
KEY_SEAT_MANAGEMENT_ENABLED = 'seat_management_enabled'
KEY_USER_REGISTRATION_ENABLED = 'user_registration_enabled'


SiteMode = Enum('SiteMode', ['public', 'admin'])
SiteMode.is_admin = lambda self: self == SiteMode.admin
SiteMode.is_public = lambda self: self == SiteMode.public


class ConfigurationError(Exception):
    pass


def init_app(app):
    app.extensions[EXTENSION_KEY] = {}

    site_mode = determine_site_mode(app)
    update_extension_value(app, KEY_SITE_MODE, site_mode)

    if site_mode.is_public():
        site_id = determine_site_id(app)
        update_extension_value(app, KEY_SITE_ID, site_id)

    user_registration_enabled = determine_user_registration_enabled(
        app, site_mode
    )
    update_extension_value(
        app, KEY_USER_REGISTRATION_ENABLED, user_registration_enabled
    )

    seat_management_enabled = determine_seat_management_enabled(app, site_mode)
    update_extension_value(
        app, KEY_SEAT_MANAGEMENT_ENABLED, seat_management_enabled
    )


def update_extension_value(app, key, value):
    """Set/replace the value value for the key in this application's
    own extension namespace.
    """
    app.extensions[EXTENSION_KEY][key] = value


# -------------------------------------------------------------------- #
# site mode


def determine_site_mode(app):
    value = app.config.get('SITE_MODE')
    if value is None:
        raise ConfigurationError('No site mode configured.')

    try:
        return SiteMode[value]
    except KeyError:
        raise ConfigurationError(f'Invalid site mode "{value}" configured.')


def get_site_mode(app=None):
    """Return the mode the site should run in."""
    return _get_config_dict(app)[KEY_SITE_MODE]


# -------------------------------------------------------------------- #
# site ID


def determine_site_id(app):
    site_id = app.config.get('SITE_ID')
    if site_id is None:
        raise ConfigurationError('No site ID configured.')

    return site_id


def get_current_site_id(app=None):
    """Return the id of the current site."""
    return _get_config_dict(app)[KEY_SITE_ID]


# -------------------------------------------------------------------- #
# user registration


def determine_user_registration_enabled(app, site_mode):
    if site_mode.is_admin():
        return False

    return app.config['USER_REGISTRATION_ENABLED']


def get_user_registration_enabled(app=None):
    """Return `True` if guests may register user accounts."""
    return _get_config_dict(app)[KEY_USER_REGISTRATION_ENABLED]


# -------------------------------------------------------------------- #
# seat management


def determine_seat_management_enabled(app, site_mode):
    if site_mode.is_admin():
        return False

    return app.config['SEAT_MANAGEMENT_ENABLED']


def get_seat_management_enabled(app=None):
    """Return `True` if users may manage seats."""
    return _get_config_dict(app)[KEY_SEAT_MANAGEMENT_ENABLED]


# -------------------------------------------------------------------- #


def _get_config_dict(app=None):
    if app is None:
        app = current_app

    return app.extensions[EXTENSION_KEY]
