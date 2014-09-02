# -*- coding: utf-8 -*-

"""
byceps.blueprints.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from importlib import import_module

from flask import current_app, render_template

from ... import config
from ...config import SiteMode
from ...util.framework import create_blueprint


navigation_modules = {
    mode: import_module('config.navigation_{}'.format(mode.name))
    for mode in SiteMode}


blueprint = create_blueprint('core', __name__)


@blueprint.app_errorhandler(403)
def forbidden(error):
    return render_template('error/forbidden.html'), 403


@blueprint.app_errorhandler(404)
def not_found(error):
    return render_template('error/not_found.html'), 404


@blueprint.app_context_processor
def inject_navigation():
    navigation_module = navigation_modules[config.get_site_mode()]
    return {
        'navigation_blocks': navigation_module.get_blocks(),
    }


@blueprint.app_template_global()
def add_page_arg(args, page):
    """Add the 'page' value.

    Used for pagination.
    """
    if args is None:
        args = {}

    args['page'] = page
    return args


@blueprint.app_template_test()
def is_current_page(nav_item_path, current_page=None):
    if current_page is None:
        return False

    first = current_page.split('.', 1)[0]
    return nav_item_path == first
