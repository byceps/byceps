"""
byceps.services.core.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from http import HTTPStatus
from typing import Any

from flask import g, redirect, url_for
import sentry_sdk

from byceps.services.brand import brand_service
from byceps.services.text_markup import text_markup_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.l10n import get_locales
from byceps.util.user_session import get_current_user


blueprint = create_blueprint('core_admin', __name__)


blueprint.add_app_template_filter(text_markup_service.render_html, 'bbcode')


@blueprint.app_context_processor
def inject_template_variables() -> dict[str, Any]:
    def get_brand_for_site(site):
        return brand_service.find_brand(site.brand_id)

    def get_brand_for_party(party):
        return brand_service.find_brand(party.brand_id)

    return {
        'get_brand_for_site': get_brand_for_site,
        'get_brand_for_party': get_brand_for_party,
    }


@blueprint.before_app_request
def prepare_request_globals() -> None:
    required_permissions = {'admin.access'}
    g.user = get_current_user(required_permissions)
    sentry_sdk.set_user({'id': str(g.user.id), 'username': g.user.screen_name})

    g.locales = get_locales()


@blueprint.get('/')
def homepage():
    if g.user.authenticated:
        url = url_for('admin_dashboard.view_global')
    else:
        url = url_for('authn_login_admin.log_in_form')

    return redirect(url, code=HTTPStatus.TEMPORARY_REDIRECT)
