# -*- coding: utf-8 -*-

"""
byceps.blueprints.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import render_template

from ...navigation import navigation
from ...util.framework import create_blueprint


blueprint = create_blueprint('core', __name__)


@blueprint.app_errorhandler(403)
def forbidden(error):
    return render_template('error/forbidden.html'), 403


@blueprint.app_errorhandler(404)
def not_found(error):
    return render_template('error/not_found.html'), 404


@blueprint.app_context_processor
def inject_navigation():
    return {
        'navigation_items': navigation.get_items(),
    }


@blueprint.app_template_test()
def is_current_page(nav_item_path, current_page=None):
    if current_page is None:
        return False

    first = current_page.split('.', 1)[0]
    return nav_item_path == first
