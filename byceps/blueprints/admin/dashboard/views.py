"""
byceps.blueprints.admin.dashboard.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, timedelta

from flask import abort

from ....services.brand import (
    service as brand_service,
    settings_service as brand_settings_service,
)
from ....services.consent import subject_service as consent_subject_service
from ....services.newsletter import service as newsletter_service
from ....services.orga import birthday_service as orga_birthday_service
from ....services.orga_team import service as orga_team_service
from ....services.party import service as party_service
from ....services.seating import (
    area_service as seating_area_service,
    seat_service,
)
from ....services.shop.order import service as shop_order_service
from ....services.shop.shop import service as shop_service
from ....services.site import service as site_service
from ....services.ticketing import ticket_service
from ....services.user import stats_service as user_stats_service
from ....util.authorization import register_permission_enum
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import permission_required

from ..user.service import get_users_created_since

from .authorization import AdminDashboardPermission


blueprint = create_blueprint('admin_dashboard', __name__)


register_permission_enum(AdminDashboardPermission)


@blueprint.get('')
@permission_required(AdminDashboardPermission.view_global)
@templated
def view_global():
    """View dashboard for global entities."""
    active_brands = brand_service.get_active_brands()

    current_sites = site_service.get_current_sites(include_brands=True)

    active_parties = party_service.get_active_parties(include_brands=True)
    active_parties_with_ticket_stats = [
        (party, ticket_service.get_ticket_sale_stats(party.id))
        for party in active_parties
    ]

    active_shops = shop_service.get_active_shops()
    active_shops_with_open_orders_counts = [
        (shop, shop_order_service.count_open_orders(shop.id))
        for shop in active_shops
    ]

    user_count = user_stats_service.count_users()

    one_week_ago = timedelta(days=7)
    recent_users = get_users_created_since(one_week_ago, limit=4)
    recent_users_count = user_stats_service.count_users_created_since(
        one_week_ago
    )

    uninitialized_user_count = user_stats_service.count_uninitialized_users()

    orgas_with_next_birthdays = list(
        orga_birthday_service.collect_orgas_with_next_birthdays(limit=3)
    )

    return {
        'active_brands': active_brands,
        'current_sites': current_sites,
        'active_parties_with_ticket_stats': active_parties_with_ticket_stats,
        'active_shops_with_open_orders_counts': active_shops_with_open_orders_counts,

        'user_count': user_count,
        'recent_users': recent_users,
        'recent_users_count': recent_users_count,
        'uninitialized_user_count': uninitialized_user_count,

        'orgas_with_next_birthdays': orgas_with_next_birthdays,
    }


@blueprint.get('/brands/<brand_id>')
@permission_required(AdminDashboardPermission.view_brand)
@templated
def view_brand(brand_id):
    """View dashboard for that brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    current_sites = site_service.get_current_sites(
        brand_id=brand.id, include_brands=True
    )

    active_parties = party_service.get_active_parties(
        brand_id=brand.id, include_brands=True
    )
    active_parties_with_ticket_stats = [
        (party, ticket_service.get_ticket_sale_stats(party.id))
        for party in active_parties
    ]

    newsletter_list_id = brand_settings_service.find_setting_value(
        brand.id, 'newsletter_list_id'
    )
    newsletter_list = None
    if newsletter_list_id:
        newsletter_list = newsletter_service.find_list(newsletter_list_id)
        newsletter_subscriber_count = (
            newsletter_service.count_subscribers_for_list(newsletter_list.id)
        )
    else:
        newsletter_subscriber_count = None

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
        'active_parties_with_ticket_stats': active_parties_with_ticket_stats,

        'newsletter_list': newsletter_list,
        'newsletter_subscriber_count': newsletter_subscriber_count,

        'consent_subjects_with_consent_counts': consent_subjects_with_consent_counts,

        'shop': shop,
        'open_order_count': open_order_count,
    }


@blueprint.get('/parties/<party_id>')
@permission_required(AdminDashboardPermission.view_party)
@templated
def view_party(party_id):
    """View dashboard for that party."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    days_until_party = (party.starts_at.date() - date.today()).days

    orga_count = orga_team_service.count_memberships_for_party(party.id)
    orga_team_count = orga_team_service.count_teams_for_party(party.id)

    seating_area_count = seating_area_service.count_areas_for_party(party.id)
    seat_count = seat_service.count_seats_for_party(party.id)

    ticket_sale_stats = ticket_service.get_ticket_sale_stats(party.id)
    tickets_checked_in = ticket_service.count_tickets_checked_in_for_party(
        party.id
    )

    return {
        'party': party,
        'days_until_party': days_until_party,

        'orga_count': orga_count,
        'orga_team_count': orga_team_count,

        'seating_area_count': seating_area_count,
        'seat_count': seat_count,

        'ticket_sale_stats': ticket_sale_stats,
        'tickets_checked_in': tickets_checked_in,
    }
