# -*- coding: utf-8 -*-

"""
byceps.util.framework
~~~~~~~~~~~~~~~~~~~~~

Framework utilities.

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from collections import namedtuple
from importlib import import_module

from flask import Blueprint, flash


# -------------------------------------------------------------------- #
# configuration


def load_config(app, environment_name):
    """Load the configuration for the specified environment from the
    corresponding module.

    The module is expected to be located in the 'config/env'
    sub-package.
    """
    module_path = 'config.env.{}'.format(environment_name)
    app.config.from_object(module_path)


# -------------------------------------------------------------------- #
# blueprints


def create_blueprint(name, import_name):
    """Create a blueprint with default folder names."""
    return Blueprint(
        name, import_name,
        static_folder='static',
        template_folder='templates')


def register_blueprint(app, name, url_prefix):
    """Register a blueprint with the application.

    The module with the given name is expected to be located inside the
    'blueprints' sub-package and to contain a blueprint instance named
    'blueprint'.
    """
    module = get_blueprint_views_module(name)
    blueprint = getattr(module, 'blueprint')
    app.register_blueprint(blueprint, url_prefix=url_prefix)


def get_blueprint_views_module(name):
    """Import and return the 'views' module located in the specified
    blueprint package.
    """
    return import_module('byceps.blueprints.{}.views'.format(name))


# -------------------------------------------------------------------- #
# message flashing


FlashMessage = namedtuple('FlashMessage',
                          ['text', 'text_is_safe', 'category', 'icon'])


def flash_error(message, *args, icon=None, text_is_safe=False):
    """Flash a message indicating an error."""
    return _flash(message, *args,
                  category='error', icon=icon, text_is_safe=text_is_safe)


def flash_notice(message, *args, icon=None, text_is_safe=False):
    """Flash a generally informational message."""
    return _flash(message, *args,
                  category='info', icon=icon, text_is_safe=text_is_safe)


def flash_success(message, *args, icon=None, text_is_safe=False):
    """Flash a message describing a successful action."""
    return _flash(message, *args,
                  category='success', icon=icon, text_is_safe=text_is_safe)


def _flash(message, *args, category=None, icon=None, text_is_safe=False):
    text = message.format(*args)

    flash_message = FlashMessage(text, text_is_safe, category, icon)

    return flash(flash_message)
