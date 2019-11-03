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


def _get_config_dict(app=None):
    if app is None:
        app = current_app

    return app.extensions[EXTENSION_KEY]
