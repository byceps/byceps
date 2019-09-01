"""
byceps.blueprints.admin.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict

from flask import abort, request

from ....services.party import service as party_service
from ....services.site import \
    service as site_service, \
    settings_service as site_settings_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import SitePermission
from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('site_admin', __name__)


permission_registry.register_enum(SitePermission)


@blueprint.route('/')
@permission_required(SitePermission.view)
@templated
def index():
    """List all sites."""
    sites = site_service.get_all_sites()

    return {
        'sites': sites,
    }


@blueprint.route('/parties/<party_id>')
@permission_required(SitePermission.view)
@templated
def index_for_party(party_id):
    """List sites and their settings for this party."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    sites = site_service.get_sites_for_party(party.id)
    settings = site_settings_service.get_settings_for_party(party.id)

    settings_by_site = _group_settings_by_site(settings)

    return {
        'party': party,
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


@blueprint.route('/for_party/<party_id>/create')
@permission_required(SitePermission.create)
@templated
def create_form(party_id, erroneous_form=None):
    """Show form to create a site for that party."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/for_party/<party_id>', methods=['POST'])
@permission_required(SitePermission.create)
def create(party_id):
    """Create a site for that party."""
    party = _get_party_or_404(party_id)

    form = CreateForm(request.form)

    if not form.validate():
        return create_form(party.id, form)

    site_id = form.id.data.strip().lower()
    title = form.title.data.strip()
    server_name = form.server_name.data.strip()
    email_config_id = form.email_config_id.data.strip()

    site = site_service.create_site(site_id, party.id, title, server_name,
                                    email_config_id)

    flash_success('Die Site "{}" wurde angelegt.', site.title)
    return redirect_to('.view', site_id=site.id)


@blueprint.route('/sites/<site_id>/update')
@permission_required(SitePermission.update)
@templated
def update_form(site_id, erroneous_form=None):
    """Show form to update the site."""
    site = _get_site_or_404(site_id)
    party = party_service.find_party(site.party_id)

    form = erroneous_form if erroneous_form else UpdateForm(obj=site)

    return {
        'party': party,
        'site': site,
        'form': form,
    }


@blueprint.route('/sites/<site_id>', methods=['POST'])
@permission_required(SitePermission.update)
def update(site_id):
    """Update the site."""
    site = _get_site_or_404(site_id)

    form = UpdateForm(request.form)
    if not form.validate():
        return update_form(site.id, form)

    title = form.title.data.strip()
    server_name = form.server_name.data.strip()
    email_config_id = form.email_config_id.data.strip()

    try:
        site = site_service.update_site(site.id, title, server_name,
                                        email_config_id)
    except site_service.UnknownSiteId:
        abort(404, 'Unknown site ID "{}".'.format(site_id))

    flash_success('Die Site "{}" wurde aktualisiert.', site.title)

    return redirect_to('.view', site_id=site.id)


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_site_or_404(site_id):
    site = site_service.find_site(site_id)

    if site is None:
        abort(404)

    return site
