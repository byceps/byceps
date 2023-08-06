"""
byceps.blueprints.site.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from flask import current_app, g, redirect, request, url_for
from flask_babel import get_locale

from byceps.services.party import party_service
from byceps.services.site import site_service
from byceps.services.text_markup import text_markup_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.l10n import get_locales
from byceps.util.user_session import get_current_user


blueprint = create_blueprint('core_site', __name__)


blueprint.add_app_template_filter(text_markup_service.render_html, 'bbcode')


@blueprint.app_template_global()
def url_for_site_file(filename, **kwargs) -> str | None:
    """Render URL for a static file local to the current site."""
    site_id = getattr(g, 'site_id', None)

    if site_id is None:
        return None

    return url_for('site_file', site_id=site_id, filename=filename, **kwargs)


@blueprint.before_app_request
def prepare_request_globals() -> None:
    site_id = current_app.config['SITE_ID']
    site = site_service.get_site(site_id)
    g.site = site
    g.site_id = site.id

    g.brand_id = site.brand_id

    party = None
    party_id = site.party_id
    if party_id is not None:
        party = party_service.get_party(party_id)
        party_id = party.id
    g.party = party
    g.party_id = party_id

    required_permissions: set[str] = set()
    g.user = get_current_user(required_permissions)

    g.locales = get_locales()
    # Must only be called *after* `g.user` is set.
    g.current_locale = get_locale()


@blueprint.app_context_processor
def inject_remote_addr() -> dict[str, Any]:
    if not g.site.is_intranet or not g.user.authenticated:
        return {}

    return {
        'remote_addr': request.remote_addr,
    }


@blueprint.get('/')
def homepage():
    """Set an optional URL path to redirect to from the root URL path (`/`).

    Important: Don't specify the target with a leading slash unless you
    really mean the root of the host.
    """
    return redirect(url_for('news.index'), code=HTTPStatus.TEMPORARY_REDIRECT)
