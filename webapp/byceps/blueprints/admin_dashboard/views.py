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

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..orga_admin import service as orga_admin_service
from ..party.models import Party
from ..ticket import service as ticket_service
from ..shop_admin import service as shop_admin_service

from .authorization import AdminDashboardPermission


blueprint = create_blueprint('admin_dashboard', __name__)


permission_registry.register_enum(AdminDashboardPermission)


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

    article_count = shop_admin_service.count_articles_for_party(party)
    open_order_count = shop_admin_service.count_open_orders_for_party(party)
    tickets_sold = ticket_service.count_tickets_for_party(party)

    return {
        'party': party,
        'days_until_party': days_until_party,

        'orga_count': orga_count,
        'orga_team_count': orga_team_count,

        'article_count': article_count,
        'open_order_count': open_order_count,
        'tickets_sold': tickets_sold,
    }
