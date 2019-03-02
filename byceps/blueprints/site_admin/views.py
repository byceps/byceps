"""
byceps.blueprints.site_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict

from flask import abort, request

from ...services.site import \
    service as site_service, \
    settings_service as site_settings_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import SitePermission


blueprint = create_blueprint('site_admin', __name__)


permission_registry.register_enum(SitePermission)


@blueprint.route('/')
@permission_required(SitePermission.view)
@templated
def index():
    """List sites and their settings."""
    sites = site_service.get_all_sites()
    settings = site_settings_service.get_all_settings()

    settings_by_site = _group_settings_by_site(settings)

    return {
        'sites': sites,
        'settings_by_site': settings_by_site,
    }


def _group_settings_by_site(settings):
    settings_by_site = defaultdict(list)

    for setting in settings:
        settings_by_site[setting.site_id].append(setting)

    return dict(settings_by_site)


@blueprint.route('/sites/<site_id>')
@permission_required(SitePermission.view)
@templated
def view(site_id):
    """Show a site's settings."""
    site = site_service.find_site(site_id)
    if site is None:
        abort(404)

    settings = site_settings_service.get_settings(site.id)

    return {
        'site': site,
        'settings': settings,
    }
