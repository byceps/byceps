"""
byceps.blueprints.common.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime
from typing import Optional

from flask import g, render_template, url_for

from .... import config
from ....services.party import service as party_service
from ....services.site import service as site_service
from ....util.authorization import (
    has_current_user_any_permission,
    has_current_user_permission,
    permission_registry,
)
from ....util.framework.blueprint import create_blueprint
from ....util.navigation import Navigation
from ....util.user_session import (
    get_current_user,
    get_locale as get_session_locale,
)

from ...admin.core.authorization import AdminPermission


blueprint = create_blueprint('core', __name__)


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
def url_for_site_file(filename, **kwargs) -> Optional[str]:
    """Render URL for a static file local to the current site."""
    site_id = getattr(g, 'site_id', None)

    if site_id is None:
        return None

    return url_for('site_file', site_id=site_id, filename=filename, **kwargs)


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
def provide_app_mode():
    app_mode = config.get_app_mode()
    g.app_mode = app_mode

    locale = get_session_locale()

    if app_mode.is_admin():
        required_permissions = {AdminPermission.access}
        g.user = get_current_user(required_permissions, locale)
    elif app_mode.is_site():
        site_id = config.get_current_site_id()
        site = site_service.get_site(site_id)
        g.site_id = site.id

        g.brand_id = site.brand_id

        party_id = site.party_id
        if party_id is not None:
            party = party_service.get_party(party_id)
            party_id = party.id
        g.party_id = party_id

        required_permissions = set()
        g.user = get_current_user(
            required_permissions, locale, party_id=party_id
        )
