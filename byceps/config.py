"""
byceps.config
~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum

from flask import current_app


STATIC_URL_PREFIX_GLOBAL = '/global'
STATIC_URL_PREFIX_BRAND = '/brand'
STATIC_URL_PREFIX_PARTY = '/party'

EXTENSION_KEY = 'byceps_config'
KEY_SITE_MODE = 'site_mode'
KEY_PARTY_ID = 'party_id'
KEY_TICKET_MANAGEMENT_ENABLED = 'ticket_management_enabled'
KEY_USER_REGISTRATION_ENABLED = 'user_registration_enabled'


SiteMode = Enum('SiteMode', ['public', 'admin'])
SiteMode.is_admin = lambda self: self == SiteMode.admin
SiteMode.is_public = lambda self: self == SiteMode.public


def init_app(app):
    app.extensions[EXTENSION_KEY] = {}

    site_mode = determine_site_mode(app)
    update_extension_value(app, KEY_SITE_MODE, site_mode)

    if site_mode.is_public():
        party_id = determine_party_id(app)
        update_extension_value(app, KEY_PARTY_ID, party_id)

    user_registration_enabled = determine_user_registration_enabled(app,
                                                                    site_mode)
    update_extension_value(app, KEY_USER_REGISTRATION_ENABLED,
                           user_registration_enabled)

    ticket_management_enabled = determine_ticket_management_enabled(app,
                                                                    site_mode)
    update_extension_value(app, KEY_TICKET_MANAGEMENT_ENABLED,
                           ticket_management_enabled)


def update_extension_value(app, key, value):
    """Set/replace the value value for the key in this application's
    own extension namespace.
    """
    app.extensions[EXTENSION_KEY][key] = value


# -------------------------------------------------------------------- #
# site mode


def determine_site_mode(app):
    value = app.config.get('MODE')
    if value is None:
        raise Exception('No site mode configured.')

    try:
        return SiteMode[value]
    except KeyError:
        raise Exception('Invalid site mode "{}" configured.'.format(value))


def get_site_mode(app=None):
    """Return the mode the site should run in."""
    return _get_config_dict(app)[KEY_SITE_MODE]


# -------------------------------------------------------------------- #
# party ID


def determine_party_id(app):
    party_id = app.config.get('PARTY')
    if party_id is None:
        raise Exception('No party configured.')

    return party_id


def get_current_party_id(app=None):
    """Return the id of the current party."""
    return _get_config_dict(app)[KEY_PARTY_ID]


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
# ticket management


def determine_ticket_management_enabled(app, site_mode):
    if site_mode.is_admin():
        return False

    return app.config['TICKET_MANAGEMENT_ENABLED']


def get_ticket_management_enabled(app=None):
    """Return `True` if users may manage tickets."""
    return _get_config_dict(app)[KEY_TICKET_MANAGEMENT_ENABLED]


# -------------------------------------------------------------------- #


def _get_config_dict(app=None):
    if app is None:
        app = current_app

    return app.extensions[EXTENSION_KEY]
