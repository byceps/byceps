# -*- coding: utf-8 -*-

"""
byceps.blueprints.admin_dashboard.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, timedelta

from flask import abort

from ...services.newsletter import service as newsletter_service
from ...services.seating import service as seating_service
from ...services.ticket import service as ticket_service
from ...util.framework import create_blueprint
from ...util.templating import templated

from ..brand import service as brand_service
from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..board_admin import service as board_admin_service
from ..news_admin import service as news_admin_service
from ..orga_admin import service as orga_admin_service
from ..party import service as party_service
from ..shop import article_service, order_service
from ..terms import service as terms_service
from ..user import service as user_service

from .authorization import AdminDashboardPermission


blueprint = create_blueprint('admin_dashboard', __name__)


permission_registry.register_enum(AdminDashboardPermission)


@blueprint.route('')
@permission_required(AdminDashboardPermission.view_global)
@templated
def view_global():
    """View dashboard for global entities."""
    brand_count = brand_service.count_brands()
    party_count = party_service.count_parties()

    orga_count = orga_admin_service.count_orgas()

    user_count  = user_service.count_users()

    one_week_ago = timedelta(days=7)
    recent_users_count = user_service.count_users_created_since(one_week_ago)

    disabled_user_count = user_service.count_disabled_users()

    orgas_with_next_birthdays = list(
        orga_admin_service.collect_orgas_with_next_birthdays(limit=3))

    return {
        'brand_count': brand_count,
        'party_count': party_count,

        'orga_count': orga_count,

        'user_count': user_count,
        'recent_users_count': recent_users_count,
        'disabled_user_count': disabled_user_count,

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

    party_count = party_service.count_parties_for_brand(brand.id)

    orga_count = orga_admin_service.count_orgas_for_brand(brand)

    news_item_count = news_admin_service.count_items_for_brand(brand)

    newsletter_subscriber_count = newsletter_service \
        .count_subscribers_for_brand(brand.id)

    current_terms_version = terms_service.get_current_version(brand.id)

    board_category_count = board_admin_service.count_categories_for_brand(brand)
    board_topic_count = board_admin_service.count_topics_for_brand(brand)
    board_posting_count = board_admin_service.count_postings_for_brand(brand)

    return {
        'brand': brand,

        'party_count': party_count,

        'orga_count': orga_count,

        'news_item_count': news_item_count,

        'newsletter_subscriber_count': newsletter_subscriber_count,

        'current_terms_version': current_terms_version,

        'board_category_count': board_category_count,
        'board_topic_count': board_topic_count,
        'board_posting_count': board_posting_count,
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

    orga_teams = orga_admin_service.get_teams_for_party(party)
    orga_team_count = len(orga_teams)
    orga_count = sum(len(team.memberships) for team in orga_teams)

    seating_area_count = seating_service.count_areas_for_party(party.id)
    seat_count = seating_service.count_seats_for_party(party.id)

    article_count = article_service.count_articles_for_party(party.id)
    open_order_count = order_service.count_open_orders_for_party(party.id)
    tickets_sold = ticket_service.count_tickets_for_party(party)

    return {
        'party': party,
        'days_until_party': days_until_party,

        'orga_count': orga_count,
        'orga_team_count': orga_team_count,

        'seating_area_count': seating_area_count,
        'seat_count': seat_count,

        'article_count': article_count,
        'open_order_count': open_order_count,

        'tickets_sold': tickets_sold,
    }
