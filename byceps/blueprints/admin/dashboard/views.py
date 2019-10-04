"""
byceps.blueprints.admin.dashboard.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, timedelta

from flask import abort

from ....services.brand import (
    service as brand_service,
    settings_service as brand_settings_service,
)
from ....services.news import service as news_service
from ....services.newsletter import service as newsletter_service
from ....services.orga import service as orga_service
from ....services.orga import birthday_service as orga_birthday_service
from ....services.orga_team import service as orga_team_service
from ....services.party import service as party_service
from ....services.seating import (
    area_service as seating_area_service,
    seat_service,
)
from ....services.shop.article import service as article_service
from ....services.shop.order import service as order_service
from ....services.shop.shop import service as shop_service
from ....services.terms import version_service as terms_version_service
from ....services.ticketing import ticket_service
from ....services.user import stats_service as user_stats_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import AdminDashboardPermission


blueprint = create_blueprint('admin_dashboard', __name__)


permission_registry.register_enum(AdminDashboardPermission)


@blueprint.route('')
@permission_required(AdminDashboardPermission.view_global)
@templated
def view_global():
    """View dashboard for global entities."""
    active_parties = party_service.get_active_parties()

    brand_count = brand_service.count_brands()
    party_count = party_service.count_parties()

    orga_count = orga_service.count_orgas()

    user_count = user_stats_service.count_users()

    one_week_ago = timedelta(days=7)
    recent_users_count = user_stats_service.count_users_created_since(
        one_week_ago
    )

    uninitialized_user_count = user_stats_service.count_uninitialized_users()

    orgas_with_next_birthdays = list(
        orga_birthday_service.collect_orgas_with_next_birthdays(limit=3))

    return {
        'active_parties': active_parties,

        'brand_count': brand_count,
        'party_count': party_count,

        'orga_count': orga_count,

        'user_count': user_count,
        'recent_users_count': recent_users_count,
        'uninitialized_user_count': uninitialized_user_count,

        'orgas_with_next_birthdays': orgas_with_next_birthdays,
    }


@blueprint.route('/brands/<brand_id>')
@permission_required(AdminDashboardPermission.view_brand)
@templated
def view_brand(brand_id):
    """View dashboard for that brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    active_parties = party_service.get_active_parties(brand_id=brand.id)

    party_count = party_service.count_parties_for_brand(brand.id)

    orga_count = orga_service.count_orgas_for_brand(brand.id)

    news_item_count = news_service.count_items_for_brand(brand.id)

    newsletter_list_id = brand_settings_service.find_setting_value(
        brand.id, 'newsletter_list_id'
    )
    newsletter_list = None
    if newsletter_list_id:
        newsletter_list = newsletter_service.find_list(newsletter_list_id)
        newsletter_subscriber_count = newsletter_service.count_subscribers_for_list(
            newsletter_list.id
        )
    else:
        newsletter_subscriber_count = None

    current_terms_version = terms_version_service.find_current_version(brand.id)

    return {
        'brand': brand,

        'active_parties': active_parties,

        'party_count': party_count,

        'orga_count': orga_count,

        'news_item_count': news_item_count,

        'newsletter_list': newsletter_list,
        'newsletter_subscriber_count': newsletter_subscriber_count,

        'current_terms_version': current_terms_version,
    }


@blueprint.route('/parties/<party_id>')
@permission_required(AdminDashboardPermission.view_party)
@templated
def view_party(party_id):
    """View dashboard for that party."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    days_until_party = (party.starts_at.date() - date.today()).days

    orga_teams = orga_team_service.get_teams_for_party(party.id)
    orga_team_count = len(orga_teams)
    orga_count = sum(len(team.memberships) for team in orga_teams)

    seating_area_count = seating_area_service.count_areas_for_party(party.id)
    seat_count = seat_service.count_seats_for_party(party.id)

    if party.shop_id:
        shop = shop_service.get_shop(party.shop_id)

        article_count = article_service.count_articles_for_shop(shop.id)
        open_order_count = order_service.count_open_orders(shop.id)
    else:
        shop = None

        article_count = 0
        open_order_count = 0

    tickets_sold = ticket_service.count_tickets_for_party(party.id)
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

        'shop': shop,
        'article_count': article_count,
        'open_order_count': open_order_count,

        'tickets_sold': tickets_sold,
        'tickets_checked_in': tickets_checked_in,
    }
