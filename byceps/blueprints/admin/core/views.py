"""
byceps.blueprints.admin.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Any

from flask import g

from ....services.brand import service as brand_service
from ....util.framework.blueprint import create_blueprint
from ....util.user_session import get_current_user
from ....util.views import redirect_to


blueprint = create_blueprint('core_admin', __name__)


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


@blueprint.get('/')
def homepage():
    if g.user.authenticated:
        return redirect_to('admin_dashboard.view_global')
    else:
        return redirect_to('authentication_login_admin.log_in_form')
