# -*- coding: utf-8 -*-

"""
byceps.blueprints.admin_dashboard.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..brand.models import Brand
from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..board_admin import service as board_admin_service
from ..news_admin import service as news_admin_service
from ..newsletter_admin import service as newsletter_admin_service
from ..orga_admin import service as orga_admin_service
from ..party.models import Party
from ..ticket import service as ticket_service
from ..seating_admin import service as seating_admin_service
from ..shop_admin import service as shop_admin_service
from ..terms import service as terms_service
from ..user.models import User

from .authorization import AdminDashboardPermission


blueprint = create_blueprint('admin_dashboard', __name__)


permission_registry.register_enum(AdminDashboardPermission)


@blueprint.route('')
@permission_required(AdminDashboardPermission.view_global)
@templated
def view_global():
    """View dashboard for global entities."""
    brand_count = Brand.query.count()
    party_count = Party.query.count()

    orga_count = orga_admin_service.count_orgas()

    user_count = User.query.count()

    return {
        'brand_count': brand_count,
        'party_count': party_count,

        'orga_count': orga_count,

        'user_count': user_count,
    }


@blueprint.route('/brands/<brand_id>')
@permission_required(AdminDashboardPermission.view_brand)
@templated
def view_brand(brand_id):
    """View dashboard for that brand."""
    brand = Brand.query.get_or_404(brand_id)

    party_count = Party.query.for_brand(brand).count()

    orga_count = orga_admin_service.count_orgas_for_brand(brand)

    news_item_count = news_admin_service.count_items_for_brand(brand)

    newsletter_subscriber_count = newsletter_admin_service \
        .count_subscribers_for_brand(brand)

    current_terms_version = terms_service.get_current_version(brand)

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
    party = Party.query.get_or_404(party_id)

    days_until_party = (party.starts_at.date() - date.today()).days

    orga_teams = orga_admin_service.get_teams_for_party(party)
    orga_team_count = len(orga_teams)
    orga_count = sum(len(team.memberships) for team in orga_teams)

    seating_area_count = seating_admin_service.count_areas_for_party(party)
    seat_count = seating_admin_service.count_seats_for_party(party)

    article_count = shop_admin_service.count_articles_for_party(party)
    open_order_count = shop_admin_service.count_open_orders_for_party(party)
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
