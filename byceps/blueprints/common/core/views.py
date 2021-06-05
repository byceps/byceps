"""
byceps.blueprints.common.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime

from flask import g, render_template

from .... import config
from ....util.authorization import (
    has_current_user_any_permission,
    has_current_user_permission,
    permission_registry,
)
from ....util.framework.blueprint import create_blueprint
from ....util.navigation import Navigation


blueprint = create_blueprint('core_common', __name__)


@blueprint.app_errorhandler(403)
def forbidden(error):
    return render_template('error/forbidden.html'), 403


@blueprint.app_errorhandler(404)
def not_found(error):
    return render_template('error/not_found.html'), 404


@blueprint.app_context_processor
def inject_template_variables():
    context = {
        'datetime': datetime,
        'now': datetime.utcnow(),
        'today': date.today(),
        'Navigation': Navigation,
        'has_current_user_any_permission': has_current_user_any_permission,
        'has_current_user_permission': has_current_user_permission,
    }

    # Make permission enums available in templates.
    for enum in permission_registry.get_enums():
        context[enum.__name__] = enum

    return context


@blueprint.app_template_global()
def add_page_arg(args, page):
    """Add the 'page' value.

    Used for pagination.
    """
    if args is None:
        args = {}

    args['page'] = page
    return args


@blueprint.before_app_request
def prepare_request_globals():
    g.app_mode = config.get_app_mode()
