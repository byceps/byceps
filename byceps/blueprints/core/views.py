"""
byceps.blueprints.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, datetime

from flask import g, render_template

from ... import config
from ...util.framework.blueprint import create_blueprint
from ...util.navigation import Navigation


blueprint = create_blueprint('core', __name__)


@blueprint.app_errorhandler(403)
def forbidden(error):
    return render_template('error/forbidden.html'), 403


@blueprint.app_errorhandler(404)
def not_found(error):
    return render_template('error/not_found.html'), 404


@blueprint.app_context_processor
def inject_template_variables():
    return {
        'datetime': datetime,
        'now': datetime.utcnow(),
        'today': date.today(),
        'Navigation': Navigation,
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


@blueprint.before_app_request
def provide_site_mode():
    g.site_mode = config.get_site_mode()
