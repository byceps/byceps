# -*- coding: utf-8 -*-

"""
byceps.blueprints.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from importlib import import_module

from flask import render_template

from ... import config
from ...config import SiteMode
from ...util.framework import create_blueprint


blueprint = create_blueprint('core', __name__)


def _get_navigation_blocks(site_mode):
    """Import navigation module for the given mode and return the blocks."""
    module_name = 'config.navigation_{}'.format(site_mode.name)
    module = import_module(module_name)
    return module.get_blocks()


NAVIGATION_BLOCKS_BY_SITE_MODE \
    = {mode: _get_navigation_blocks(mode) for mode in SiteMode}


@blueprint.app_errorhandler(403)
def forbidden(error):
    return render_template('error/forbidden.html'), 403


@blueprint.app_errorhandler(404)
def not_found(error):
    return render_template('error/not_found.html'), 404


@blueprint.app_context_processor
def inject_navigation():
    navigation_blocks = NAVIGATION_BLOCKS_BY_SITE_MODE[config.get_site_mode()]
    return {
        'navigation_blocks': navigation_blocks,
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
    return (current_page is not None) \
            and (nav_item_path == current_page)
