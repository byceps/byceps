"""
byceps.services.core.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any

from flask import current_app, g, request, Response, url_for
from flask_babel import get_locale
import sentry_sdk

from byceps.services.party import party_service
from byceps.services.party.models import Party
from byceps.services.site import site_service
from byceps.services.site.models import Site
from byceps.services.text_markup import text_markup_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.l10n import get_locales
from byceps.util.user_session import get_current_user


blueprint = create_blueprint('core_site', __name__)


blueprint.add_app_template_filter(text_markup_service.render_html, 'bbcode')


@blueprint.app_template_global()
def url_for_site_file(filename, **kwargs) -> str | None:
    """Render URL for a static file local to the current site."""
    site = getattr(g, 'site', None)
    if not site:
        return None

    return url_for('site_file', site_id=site.id, filename=filename, **kwargs)


@blueprint.before_app_request
def prepare_request_globals():
    site = _get_site()
    if not site.enabled:
        return Response(status=404)

    g.site = site
    sentry_sdk.set_tag('site_id', site.id)

    sentry_sdk.set_tag('brand_id', site.brand_id)

    party = _get_party(site)
    g.party = party
    sentry_sdk.set_tag('party_id', party.id if party else None)

    required_permissions: set[str] = set()
    g.user = get_current_user(required_permissions)
    sentry_sdk.set_user({'id': str(g.user.id), 'username': g.user.screen_name})

    g.locales = get_locales()
    # Must only be called *after* `g.user` is set.
    g.current_locale = get_locale()


def _get_site() -> Site:
    return site_service.get_site(current_app.site_id)


def _get_party(site: Site) -> Party | None:
    if site.party_id is None:
        return None

    return party_service.get_party(site.party_id)


@blueprint.app_context_processor
def inject_remote_addr() -> dict[str, Any]:
    if not g.site.is_intranet or not g.user.authenticated:
        return {}

    return {
        'remote_addr': request.remote_addr,
    }
