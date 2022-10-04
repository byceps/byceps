"""
byceps.blueprints.common.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime
from typing import Any

from flask import g, render_template

from .... import config
from ....util.authorization import (
    has_current_user_any_permission,
    has_current_user_permission,
)
from ....util.framework.blueprint import create_blueprint
from ....util.navigation import Navigation


blueprint = create_blueprint('core_common', __name__)


@blueprint.app_errorhandler(403)
def forbidden(error) -> tuple[str, int]:
    return render_template('error/forbidden.html'), 403


@blueprint.app_errorhandler(404)
def not_found(error) -> tuple[str, int]:
    return render_template('error/not_found.html'), 404


@blueprint.app_context_processor
def inject_template_variables() -> dict[str, Any]:
    return {
        'datetime': datetime,
        'now': datetime.utcnow(),
        'today': date.today(),
        'Navigation': Navigation,
        'has_current_user_any_permission': has_current_user_any_permission,
        'has_current_user_permission': has_current_user_permission,
    }


@blueprint.app_template_global()
def add_page_arg(args, page) -> dict[str, Any]:
    """Add the 'page' value.

    Used for pagination.
    """
    if args is None:
        args = {}

    args['page'] = page
    return args


@blueprint.before_app_request
def prepare_request_globals() -> None:
    g.app_mode = config.get_app_mode()
