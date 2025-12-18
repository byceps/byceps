"""
byceps.services.dashboard.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
from datetime import date, timedelta

from flask import abort

from byceps.services.board import board_service
from byceps.services.brand import brand_service
from byceps.services.brand.models import Brand
from byceps.services.consent import consent_subject_service
from byceps.services.demo_data import demo_data_service
from byceps.services.guest_server import (
    guest_server_domain_service,
    guest_server_service,
)
from byceps.services.news import news_channel_service
from byceps.services.orga import orga_birthday_service
from byceps.services.orga_team import orga_team_service
from byceps.services.party import party_service
from byceps.services.party.models import Party, PartyWithBrand
from byceps.services.seating import seat_service, seating_area_service
from byceps.services.shop.order import order_service as shop_order_service
from byceps.services.shop.shop import shop_service
from byceps.services.shop.storefront import storefront_service
from byceps.services.site import site_service
from byceps.services.ticketing import ticket_service
from byceps.services.user import user_service, user_stats_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required


blueprint = create_blueprint('admin_dashboard', __name__)


@blueprint.get('')
@permission_required('admin.access')
@templated
def view_global():
    """View dashboard for global entities."""
    active_brands = brand_service.get_active_brands()

    current_parties = _get_current_parties(active_brands)
    current_parties_with_brand = _add_brands_to_parties(
        current_parties, active_brands
    )
    current_parties_with_stats = [
        (
            party,
            ticket_service.get_ticket_sale_stats(party),
            seat_service.get_seat_utilization(party.id),
        )
        for party in current_parties_with_brand
    ]

    all_brands_by_id = {
        brand.id: brand for brand in brand_service.get_all_brands()
    }
    active_shops = shop_service.get_active_shops()
    active_shops_with_brands_and_open_orders_counts = [
        (
            shop,
            all_brands_by_id[shop.brand_id],
            shop_order_service.count_open_orders(shop.id),
        )
        for shop in active_shops
    ]

    demo_data_exists = (
        all_brands_by_id or demo_data_service.does_demo_data_exist()
    )

    one_week_ago = timedelta(days=7)
    recent_users = user_service.get_users_created_since(one_week_ago, limit=4)
    recent_users_count = user_stats_service.count_users_created_since(
        one_week_ago
    )

    uninitialized_user_count = user_stats_service.count_uninitialized_users()

    orgas_with_next_birthdays = list(
        orga_birthday_service.collect_orgas_with_next_birthdays(limit=3)
    )

    return {
        'demo_data_exists': demo_data_exists,
        'active_brands': active_brands,
        'current_parties_with_stats': current_parties_with_stats,
        'active_shops_with_brands_and_open_orders_counts': active_shops_with_brands_and_open_orders_counts,
        'recent_users': recent_users,
        'recent_users_count': recent_users_count,
        'uninitialized_user_count': uninitialized_user_count,
        'orgas_with_next_birthdays': orgas_with_next_birthdays,
    }


def _get_current_parties(brands: Iterable[Brand]) -> list[Party]:
    brand_parties = (
        brand_service.find_current_party(brand.id) for brand in brands
    )
    parties = [party for party in brand_parties if party is not None]
    parties.sort(key=lambda party: party.starts_at)
    return parties


def _add_brands_to_parties(
    parties: Iterable[Party], brands: Iterable[Brand]
) -> list[PartyWithBrand]:
    brands_by_id = {brand.id: brand for brand in brands}

    parties_and_brands = (
        (party, brands_by_id[party.brand_id]) for party in parties
    )

    return [
        party_service.to_party_with_brand(party, brand)
        for party, brand in parties_and_brands
    ]


@blueprint.get('/brands/<brand_id>')
@permission_required('brand.view')
@templated
def view_brand(brand_id):
    """View dashboard for that brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    current_sites = site_service.get_current_sites(
        brand_id=brand.id, include_brands=True
    )

    current_party = brand_service.find_current_party(brand.id)
    if current_party:
        current_party_with_brand = party_service.to_party_with_brand(
            current_party, brand
        )
        current_party_with_stats = (
            current_party_with_brand,
            ticket_service.get_ticket_sale_stats(current_party),
            seat_service.get_seat_utilization(current_party.id),
        )
    else:
        current_party_with_stats = None

    active_news_channels = news_channel_service.get_channels_for_brand(
        brand.id, only_non_archived=True
    )

    consent_subject_ids = (
        consent_subject_service.get_subject_ids_required_for_brand(brand.id)
    )
    consent_subjects_to_consent_counts = (
        consent_subject_service.get_subjects_with_consent_counts(
            limit_to_subject_ids=consent_subject_ids
        )
    )
    consent_subjects_with_consent_counts = sorted(
        consent_subjects_to_consent_counts.items(), key=lambda x: x[0].title
    )

    shop = shop_service.find_shop_for_brand(brand.id)
    if shop is not None:
        open_order_count = shop_order_service.count_open_orders(shop.id)
    else:
        open_order_count = None

    return {
        'brand': brand,
        'current_sites': current_sites,
        'current_party_with_stats': current_party_with_stats,
        'active_news_channels': active_news_channels,
        'consent_subjects_with_consent_counts': consent_subjects_with_consent_counts,
        'shop': shop,
        'open_order_count': open_order_count,
    }


@blueprint.get('/parties/<party_id>')
@permission_required('party.view')
@templated
def view_party(party_id):
    """View dashboard for that party."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    days = party_service.get_party_days(party)

    days_until_party = (party.starts_at.date() - date.today()).days

    orga_count = orga_team_service.count_memberships_for_party(party.id)
    orga_team_count = orga_team_service.count_teams_for_party(party.id)

    seating_area_count = seating_area_service.count_areas_for_party(party.id)
    seat_count = seat_service.count_seats_for_party(party.id)

    ticket_sale_stats = ticket_service.get_ticket_sale_stats(party)
    tickets_checked_in = ticket_service.count_tickets_checked_in_for_party(
        party.id
    )

    seat_utilization = seat_service.get_seat_utilization(party.id)

    guest_servers = guest_server_service.get_all_servers_for_party(party.id)
    guest_server_quantities_by_status = (
        guest_server_domain_service.get_server_quantities_by_status(
            guest_servers
        )
    )

    return {
        'party': party,
        'days': days,
        'days_until_party': days_until_party,
        'orga_count': orga_count,
        'orga_team_count': orga_team_count,
        'seating_area_count': seating_area_count,
        'seat_count': seat_count,
        'ticket_sale_stats': ticket_sale_stats,
        'tickets_checked_in': tickets_checked_in,
        'seat_utilization': seat_utilization,
        'guest_server_quantities_by_status': guest_server_quantities_by_status,
    }


@blueprint.get('/sites/<site_id>')
@permission_required('site.view')
@templated
def view_site(site_id):
    """View dashboard for that site."""
    site = site_service.find_site(site_id)
    if site is None:
        abort(404)

    news_channels = news_channel_service.get_channels(site.news_channel_ids)

    if site.board_id:
        board = board_service.find_board(site.board_id)
    else:
        board = None

    if site.storefront_id:
        storefront = storefront_service.get_storefront(site.storefront_id)
    else:
        storefront = None

    return {
        'site': site,
        'news_channels': news_channels,
        'board': board,
        'storefront': storefront,
    }
