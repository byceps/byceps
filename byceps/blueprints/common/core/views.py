"""
byceps.blueprints.common.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, datetime
from typing import Optional

from flask import g, render_template, url_for

from .... import config
from ....services.party import service as party_service
from ....services.site import service as site_service
from ....util.framework.blueprint import create_blueprint
from ....util.navigation import Navigation

from ..authentication import service as authentication_blueprint_service


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


@blueprint.app_template_test()
def is_current_page(nav_item_path, current_page=None):
    return (current_page is not None) and (nav_item_path == current_page)


@blueprint.before_app_request
def provide_app_mode():
    # app mode
    app_mode = config.get_app_mode()
    g.app_mode = app_mode

    # site ID
    site_id = None
    if app_mode.is_site():
        site_id = config.get_current_site_id()
        g.site_id = site_id

    # current party and brand
    party_id = None
    if app_mode.is_site():
        site = site_service.get_site(site_id)

        g.brand_id = site.brand_id

        party_id = site.party_id
        if party_id is not None:
            party = party_service.get_party(party_id)
            party_id = party.id
        g.party_id = party_id

    # current user
    is_admin_mode = app_mode.is_admin()
    g.current_user = authentication_blueprint_service.get_current_user(
        is_admin_mode, party_id=party_id
    )
