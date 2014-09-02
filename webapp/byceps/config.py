# -*- coding: utf-8 -*-

"""
byceps.config
~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from enum import Enum

from flask import current_app


EXTENSION_KEY = 'byceps'
KEY_SITE_MODE = 'site_mode'


SiteMode = Enum('SiteMode', ['public', 'admin'])


def init_app(app):
    app.extensions[EXTENSION_KEY] = {
        KEY_SITE_MODE: determine_site_mode(app),
    }


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


def _get_config_dict(app=None):
    if app is None:
        app = current_app

    return app.extensions[EXTENSION_KEY]
