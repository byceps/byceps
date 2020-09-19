"""
byceps.blueprints.admin.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.board import board_service
from ....services.brand import service as brand_service
from ....services.news import channel_service as news_channel_service
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

from ...common.authorization.decorators import permission_required
from ...common.authorization.registry import permission_registry

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
    sites.sort(key=lambda site: (site.title, site.party_id))

    brands = brand_service.get_all_brands()
    brands.sort(key=lambda brand: brand.title)

    brands_by_id = {brand.id: brand for brand in brands}

    parties = party_service.get_all_parties()
    party_titles_by_id = {p.id: p.title for p in parties}

    storefronts_by_site_id = _get_storefronts_by_site_id(sites)

    return {
        'sites': sites,
        'brands': brands,
        'brands_by_id': brands_by_id,
        'party_titles_by_id': party_titles_by_id,
        'storefronts_by_site_id': storefronts_by_site_id,
    }


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

    brand = brand_service.find_brand(site.brand_id)

    if site.news_channel_id:
        news_channel = news_channel_service.find_channel(site.news_channel_id)
    else:
        news_channel = None

    if site.board_id:
        board = board_service.find_board(site.board_id)
    else:
        board = None

    if site.storefront_id:
        storefront = storefront_service.get_storefront(site.storefront_id)
        shop = shop_service.get_shop(storefront.shop_id)
    else:
        storefront = None
        shop = None

    settings = site_settings_service.get_settings(site.id)

    return {
        'site': site,
        'brand': brand,
        'news_channel': news_channel,
        'board': board,
        'shop': shop,
        'storefront': storefront,
        'settings': settings,
    }


@blueprint.route('/sites/create/for_brand/<brand_id>')
@permission_required(SitePermission.create)
@templated
def create_form(brand_id, erroneous_form=None):
    """Show form to create a site."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else CreateForm()
    form.set_email_config_choices()
    form.set_party_choices(brand.id)
    form.set_board_choices(brand.id)
    form.set_news_channel_choices(brand.id)
    form.set_storefront_choices()

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.route('/sites/for_brand/<brand_id>', methods=['POST'])
@permission_required(SitePermission.create)
def create(brand_id):
    """Create a site."""
    brand = _get_brand_or_404(brand_id)

    form = CreateForm(request.form)
    form.set_email_config_choices()
    form.set_party_choices(brand.id)
    form.set_board_choices(brand.id)
    form.set_news_channel_choices(brand.id)
    form.set_storefront_choices()

    if not form.validate():
        return create_form(brand_id, form)

    site_id = form.id.data.strip().lower()
    title = form.title.data.strip()
    server_name = form.server_name.data.strip()
    email_config_id = form.email_config_id.data
    party_id = form.party_id.data
    enabled = form.enabled.data
    user_account_creation_enabled = form.user_account_creation_enabled.data
    login_enabled = form.login_enabled.data
    news_channel_id = form.news_channel_id.data.strip()
    if not news_channel_id:
        news_channel_id = None
    board_id = form.board_id.data.strip()
    if not board_id:
        board_id = None
    storefront_id = form.storefront_id.data.strip()
    if not storefront_id:
        storefront_id = None

    if party_id:
        party = party_service.find_party(party_id)
        if not party:
            flash_error(f'Die Party-ID "{party_id}" ist unbekannt.')
            return create_form(brand_id, form)
    else:
        party_id = None

    site = site_service.create_site(
        site_id,
        title,
        server_name,
        brand.id,
        email_config_id,
        enabled=enabled,
        user_account_creation_enabled=user_account_creation_enabled,
        login_enabled=login_enabled,
        party_id=party_id,
        board_id=board_id,
        news_channel_id=news_channel_id,
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
    form.set_brand_choices()
    form.set_email_config_choices()
    form.set_party_choices(site.brand_id)
    form.set_board_choices(site.brand_id)
    form.set_news_channel_choices(site.brand_id)
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
    form.set_brand_choices()
    form.set_email_config_choices()
    form.set_party_choices(site.brand_id)
    form.set_board_choices(site.brand_id)
    form.set_news_channel_choices(site.brand_id)
    form.set_storefront_choices()

    if not form.validate():
        return update_form(site.id, form)

    title = form.title.data.strip()
    server_name = form.server_name.data.strip()
    brand_id = form.brand_id.data
    email_config_id = form.email_config_id.data
    party_id = form.party_id.data
    enabled = form.enabled.data
    user_account_creation_enabled = form.user_account_creation_enabled.data
    login_enabled = form.login_enabled.data
    news_channel_id = form.news_channel_id.data.strip()
    if not news_channel_id:
        news_channel_id = None
    board_id = form.board_id.data.strip()
    if not board_id:
        board_id = None
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
            brand_id,
            email_config_id,
            party_id,
            enabled,
            user_account_creation_enabled,
            login_enabled,
            news_channel_id,
            board_id,
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


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand
