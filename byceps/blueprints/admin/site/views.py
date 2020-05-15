"""
byceps.blueprints.admin.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.party import service as party_service
from ....services.shop.shop import service as shop_service
from ....services.shop.storefront import service as storefront_service
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

    shops_by_site_id = _get_shops_by_site_id(sites)
    storefronts_by_site_id = _get_storefronts_by_site_id(sites)

    sites.sort(key=lambda site: (site.title, site.party_id))

    return {
        'sites': sites,
        'party_titles_by_id': party_titles_by_id,
        'shops_by_site_id': shops_by_site_id,
        'storefronts_by_site_id': storefronts_by_site_id,
    }


def _get_shops_by_site_id(sites):
    shop_ids = {site.shop_id for site in sites if site.shop_id is not None}
    shops = shop_service.find_shops(shop_ids)
    shops_by_id = {shop.id: shop for shop in shops}
    return {site.id: shops_by_id.get(site.shop_id) for site in sites}


def _get_storefronts_by_site_id(sites):
    storefront_ids = {
        site.storefront_id for site in sites if site.storefront_id is not None
    }
    storefronts = storefront_service.find_storefronts(storefront_ids)
    storefronts_by_id = {
        storefront.id: storefront for storefront in storefronts
    }
    return {
        site.id: storefronts_by_id.get(site.storefront_id) for site in sites
    }


@blueprint.route('/sites/<site_id>')
@permission_required(SitePermission.view)
@templated
def view(site_id):
    """Show a site's settings."""
    site = site_service.find_site(site_id)
    if site is None:
        abort(404)

    if site.shop_id:
        shop = shop_service.get_shop(site.shop_id)
    else:
        shop = None

    if site.storefront_id:
        storefront = storefront_service.get_storefront(site.storefront_id)
    else:
        storefront = None

    settings = site_settings_service.get_settings(site.id)

    return {
        'site': site,
        'shop': shop,
        'storefront': storefront,
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
    form.set_shop_choices()
    form.set_storefront_choices()

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
    form.set_shop_choices()
    form.set_storefront_choices()

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
    shop_id = form.shop_id.data.strip()
    if not shop_id:
        shop_id = None
    storefront_id = form.storefront_id.data.strip()
    if not storefront_id:
        storefront_id = None

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
        shop_id=shop_id,
        storefront_id=storefront_id,
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
    form.set_shop_choices()
    form.set_storefront_choices()

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
    form.set_shop_choices()
    form.set_storefront_choices()

    if not form.validate():
        return update_form(site.id, form)

    title = form.title.data.strip()
    server_name = form.server_name.data.strip()
    email_config_id = form.email_config_id.data
    party_id = form.party_id.data
    enabled = form.enabled.data
    user_account_creation_enabled = form.user_account_creation_enabled.data
    login_enabled = form.login_enabled.data
    shop_id = form.shop_id.data.strip()
    if not shop_id:
        shop_id = None
    storefront_id = form.storefront_id.data.strip()
    if not storefront_id:
        storefront_id = None
    archived = form.archived.data

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
            shop_id,
            storefront_id,
            archived,
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
