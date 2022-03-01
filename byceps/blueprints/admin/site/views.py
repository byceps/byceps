"""
byceps.blueprints.admin.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
import dataclasses
from typing import Iterable, Iterator

from flask import abort, request
from flask_babel import gettext

from ....services.board import board_service
from ....services.brand import service as brand_service
from ....services.brand.transfer.models import Brand
from ....services.news import channel_service as news_channel_service
from ....services.party import service as party_service
from ....services.shop.shop import service as shop_service
from ....services.shop.storefront import service as storefront_service
from ....services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)
from ....services.site import (
    service as site_service,
    settings_service as site_settings_service,
)
from ....services.site.transfer.models import Site, SiteWithBrand
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, redirect_to, respond_no_content

from .forms import AddNewsChannelForm, CreateForm, UpdateForm


blueprint = create_blueprint('site_admin', __name__)


@blueprint.get('/')
@permission_required('site.view')
@templated
def index():
    """List all sites."""
    brands = brand_service.get_all_brands()
    brands.sort(key=lambda brand: brand.title)

    sites = site_service.get_all_sites()
    sites = list(_sites_to_sites_with_brand(sites, brands))
    sites.sort(key=lambda site: (site.title, site.party_id))

    parties = party_service.get_all_parties()
    party_titles_by_id = {p.id: p.title for p in parties}

    storefronts_by_id = _get_storefronts_by_id(sites)

    return {
        'sites': sites,
        'brands': brands,
        'party_titles_by_id': party_titles_by_id,
        'storefronts_by_id': storefronts_by_id,
    }


@blueprint.get('/for_brand/<brand_id>')
@permission_required('site.view')
@templated
def index_for_brand(brand_id):
    """List sites for this brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    sites = site_service.get_sites_for_brand(brand.id)
    sites = [_site_to_site_with_brand(site, brand) for site in sites]
    sites.sort(key=lambda site: (site.title, site.party_id))

    parties = party_service.get_all_parties()
    party_titles_by_id = {p.id: p.title for p in parties}

    storefronts_by_id = _get_storefronts_by_id(sites)

    return {
        'sites': sites,
        'brand': brand,
        'party_titles_by_id': party_titles_by_id,
        'storefronts_by_id': storefronts_by_id,
    }


def _sites_to_sites_with_brand(
    sites: Iterable[Site], brands: Iterable[Brand]
) -> Iterator[SiteWithBrand]:
    brands_by_id = {brand.id: brand for brand in brands}

    for site in sites:
        brand = brands_by_id[site.brand_id]
        yield _site_to_site_with_brand(site, brand)


def _site_to_site_with_brand(site: Site, brand: Brand) -> SiteWithBrand:
    site_tuple = dataclasses.astuple(site)
    brand_tuple = (brand,)

    return SiteWithBrand(*(site_tuple + brand_tuple))


def _get_storefronts_by_id(sites) -> dict[StorefrontID, Storefront]:
    storefront_ids = {
        site.storefront_id for site in sites if site.storefront_id is not None
    }
    storefronts = storefront_service.find_storefronts(storefront_ids)
    return {storefront.id: storefront for storefront in storefronts}


@blueprint.get('/sites/<site_id>')
@permission_required('site.view')
@templated
def view(site_id):
    """Show a site's settings."""
    site = site_service.find_site(site_id)
    if site is None:
        abort(404)

    brand = brand_service.find_brand(site.brand_id)

    news_channels = news_channel_service.get_channels(site.news_channel_ids)

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
        'news_channels': news_channels,
        'board': board,
        'shop': shop,
        'storefront': storefront,
        'settings': settings,
    }


@blueprint.get('/sites/create/for_brand/<brand_id>')
@permission_required('site.create')
@templated
def create_form(brand_id, erroneous_form=None):
    """Show form to create a site."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else CreateForm()
    _fill_in_common_form_choices(form, brand.id)

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.post('/sites/for_brand/<brand_id>')
@permission_required('site.create')
def create(brand_id):
    """Create a site."""
    brand = _get_brand_or_404(brand_id)

    form = CreateForm(request.form)
    _fill_in_common_form_choices(form, brand.id)

    if not form.validate():
        return create_form(brand_id, form)

    site_id = form.id.data.strip().lower()
    title = form.title.data.strip()
    server_name = form.server_name.data.strip()
    party_id = form.party_id.data
    enabled = form.enabled.data
    user_account_creation_enabled = form.user_account_creation_enabled.data
    login_enabled = form.login_enabled.data
    board_id = form.board_id.data.strip() or None
    storefront_id = form.storefront_id.data.strip() or None

    if party_id:
        party = party_service.find_party(party_id)
        if not party:
            flash_error(
                gettext(
                    'Party ID "%(party_id)s" is unknown.',
                    party_id=party_id,
                )
            )
            return create_form(brand_id, form)
    else:
        party_id = None

    site = site_service.create_site(
        site_id,
        title,
        server_name,
        brand.id,
        enabled=enabled,
        user_account_creation_enabled=user_account_creation_enabled,
        login_enabled=login_enabled,
        party_id=party_id,
        board_id=board_id,
        storefront_id=storefront_id,
    )

    flash_success(
        gettext('Site "%(title)s" has been created.', title=site.title)
    )

    return redirect_to('.view', site_id=site.id)


@blueprint.get('/sites/<site_id>/update')
@permission_required('site.update')
@templated
def update_form(site_id, erroneous_form=None):
    """Show form to update the site."""
    site = _get_site_or_404(site_id)

    form = erroneous_form if erroneous_form else UpdateForm(obj=site)
    form.set_brand_choices()
    _fill_in_common_form_choices(form, site.brand_id)

    return {
        'site': site,
        'form': form,
    }


@blueprint.post('/sites/<site_id>')
@permission_required('site.update')
def update(site_id):
    """Update the site."""
    site = _get_site_or_404(site_id)

    form = UpdateForm(request.form)
    form.set_brand_choices()
    _fill_in_common_form_choices(form, site.brand_id)

    if not form.validate():
        return update_form(site.id, form)

    title = form.title.data.strip()
    server_name = form.server_name.data.strip()
    brand_id = form.brand_id.data
    party_id = form.party_id.data
    enabled = form.enabled.data
    user_account_creation_enabled = form.user_account_creation_enabled.data
    login_enabled = form.login_enabled.data
    board_id = form.board_id.data.strip() or None
    storefront_id = form.storefront_id.data.strip() or None
    archived = form.archived.data

    if party_id:
        party = party_service.find_party(party_id)
        if not party:
            flash_error(
                gettext(
                    'Party ID "%(party_id)s" is unknown.',
                    party_id=party_id,
                )
            )
            return update_form(site.id, form)
    else:
        party_id = None

    try:
        site = site_service.update_site(
            site.id,
            title,
            server_name,
            brand_id,
            party_id,
            enabled,
            user_account_creation_enabled,
            login_enabled,
            board_id,
            storefront_id,
            archived,
        )
    except site_service.UnknownSiteId:
        abort(404, f'Unknown site ID "{site_id}".')

    flash_success(
        gettext('Site "%(title)s" has been updated.', title=site.title)
    )

    return redirect_to('.view', site_id=site.id)


def _fill_in_common_form_choices(form, brand_id):
    form.set_party_choices(brand_id)
    form.set_board_choices(brand_id)
    form.set_storefront_choices()


# -------------------------------------------------------------------- #
# news channels


@blueprint.get('/sites/<site_id>/news_channels/add')
@permission_required('site.update')
@templated
def add_news_channel_form(site_id, erroneous_form=None):
    """Show form to add a news channel to the site."""
    site = _get_site_or_404(site_id)

    form = erroneous_form if erroneous_form else AddNewsChannelForm()
    form.set_news_channel_choices(site.brand_id)

    return {
        'site': site,
        'form': form,
    }


@blueprint.post('/sites/<site_id>/news_channels')
@permission_required('site.update')
def add_news_channel(site_id):
    """Add a news channel to the site."""
    site = _get_site_or_404(site_id)

    form = AddNewsChannelForm(request.form)
    form.set_news_channel_choices(site.brand_id)

    if not form.validate():
        return add_news_channel_form(site.id, form)

    news_channel_id = form.news_channel_id.data
    news_channel = news_channel_service.get_channel(news_channel_id)

    site_service.add_news_channel(site.id, news_channel.id)

    flash_success(
        gettext(
            'News channel "%(news_channel_id)s" has been added to site "%(site_title)s".',
            news_channel_id=news_channel.id,
            site_title=site.title,
        )
    )

    return redirect_to('.view', site_id=site.id)


@blueprint.delete('/sites/<site_id>/news_channels/<news_channel_id>')
@permission_required('site.update')
@respond_no_content
def remove_news_channel(site_id, news_channel_id):
    """Remove the news channel from the site."""
    site = _get_site_or_404(site_id)

    news_channel = news_channel_service.find_channel(news_channel_id)
    if news_channel is None:
        abort(404)

    news_channel_id = news_channel.id

    site_service.remove_news_channel(site.id, news_channel.id)

    flash_success(
        gettext(
            'News channel "%(news_channel_id)s" has been removed from site "%(site_title)s".',
            news_channel_id=news_channel.id,
            site_title=site.title,
        )
    )


# -------------------------------------------------------------------- #


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
