"""
byceps.blueprints.admin.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.party import service as party_service
from ....services.site import (
    service as site_service,
    settings_service as site_settings_service,
)
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
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

    parties = party_service.get_all_parties()
    party_titles_by_id = {p.id: p.title for p in parties}

    sites.sort(key=lambda site: (site.title, site.party_id))

    return {
        'sites': sites,
        'party_titles_by_id': party_titles_by_id,
    }


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


@blueprint.route('/sites/create')
@permission_required(SitePermission.create)
@templated
def create_form(erroneous_form=None):
    """Show form to create a site."""
    party_id = request.args.get('party_id')

    form = erroneous_form if erroneous_form else CreateForm(party_id=party_id)
    form.set_email_config_choices()
    form.set_party_choices()

    return {
        'form': form,
    }


@blueprint.route('/sites', methods=['POST'])
@permission_required(SitePermission.create)
def create():
    """Create a site."""
    form = CreateForm(request.form)
    form.set_email_config_choices()
    form.set_party_choices()

    if not form.validate():
        return create_form(form)

    site_id = form.id.data.strip().lower()
    title = form.title.data.strip()
    server_name = form.server_name.data.strip()
    email_config_id = form.email_config_id.data
    party_id = form.party_id.data
    enabled = form.enabled.data
    user_account_creation_enabled = form.user_account_creation_enabled.data
    login_enabled = form.login_enabled.data

    if party_id:
        party = party_service.find_party(party_id)
        if not party:
            flash_error(f'Die Party-ID "{party_id}" ist unbekannt.')
            return create_form(form)
    else:
        party_id = None

    site = site_service.create_site(
        site_id,
        title,
        server_name,
        email_config_id,
        enabled,
        user_account_creation_enabled,
        login_enabled,
        party_id=party_id,
    )

    flash_success(f'Die Site "{site.title}" wurde angelegt.')
    return redirect_to('.view', site_id=site.id)


@blueprint.route('/sites/<site_id>/update')
@permission_required(SitePermission.update)
@templated
def update_form(site_id, erroneous_form=None):
    """Show form to update the site."""
    site = _get_site_or_404(site_id)

    form = erroneous_form if erroneous_form else UpdateForm(obj=site)
    form.set_email_config_choices()
    form.set_party_choices()

    return {
        'site': site,
        'form': form,
    }


@blueprint.route('/sites/<site_id>', methods=['POST'])
@permission_required(SitePermission.update)
def update(site_id):
    """Update the site."""
    site = _get_site_or_404(site_id)

    form = UpdateForm(request.form)
    form.set_email_config_choices()
    form.set_party_choices()

    if not form.validate():
        return update_form(site.id, form)

    title = form.title.data.strip()
    server_name = form.server_name.data.strip()
    email_config_id = form.email_config_id.data
    party_id = form.party_id.data
    enabled = form.enabled.data
    user_account_creation_enabled = form.user_account_creation_enabled.data
    login_enabled = form.login_enabled.data

    if party_id:
        party = party_service.find_party(party_id)
        if not party:
            flash_error(f'Die Party-ID "{party_id}" ist unbekannt.')
            return update_form(site.id, form)
    else:
        party_id = None

    try:
        site = site_service.update_site(
            site.id,
            title,
            server_name,
            email_config_id,
            party_id,
            enabled,
            user_account_creation_enabled,
            login_enabled,
        )
    except site_service.UnknownSiteId:
        abort(404, f'Unknown site ID "{site_id}".')

    flash_success(f'Die Site "{site.title}" wurde aktualisiert.')

    return redirect_to('.view', site_id=site.id)


def _get_site_or_404(site_id):
    site = site_service.find_site(site_id)

    if site is None:
        abort(404)

    return site
