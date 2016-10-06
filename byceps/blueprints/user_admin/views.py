# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict

from flask import abort, request

from ...services.authorization import service as authorization_service
from ...services.newsletter import service as newsletter_service
from ...services.party import service as party_service
from ...services.shop.order import service as order_service
from ...services.ticket import service as ticket_service
from ...services.user_badge import service as badge_service
from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..user import service as user_service

from .authorization import UserPermission
from . import service
from .service import UserEnabledFilter


blueprint = create_blueprint('user_admin', __name__)


permission_registry.register_enum(UserPermission)


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/pages/<int:page>')
@permission_required(UserPermission.list)
@templated
def index(page):
    """List users."""
    per_page = request.args.get('per_page', type=int, default=20)
    search_term = request.args.get('search_term', default='').strip()

    if search_term:
        # Enabled filter argument is ignored if search term is given.
        only = None
        enabled_filter = None
    else:
        only = request.args.get('only')
        enabled_filter = UserEnabledFilter.__members__.get(only)

    users = service.get_users_paginated(page, per_page,
                                        search_term=search_term,
                                        enabled_filter=enabled_filter)

    total_enabled = user_service.count_enabled_users()
    total_disabled = user_service.count_disabled_users()
    total_overall = total_enabled + total_disabled

    return {
        'users': users,
        'total_enabled': total_enabled,
        'total_disabled': total_disabled,
        'total_overall': total_overall,
        'search_term': search_term,
        'only': only,
    }


@blueprint.route('/<uuid:user_id>')
@permission_required(UserPermission.view)
@templated
def view(user_id):
    """Show a user's interal profile."""
    user = _get_user_or_404(user_id)

    badges = badge_service.get_badges_for_user(user.id)

    orders = order_service.get_orders_placed_by_user(user.id)

    tickets = ticket_service.find_tickets_related_to_user(user.id)

    tickets_by_party = _group_tickets_by_party(tickets)

    parties_and_tickets = []
    for party in sorted(tickets_by_party.keys(),
                        key=lambda p: p.starts_at, reverse=True):
        tickets_sorted = sorted(tickets, key=lambda t: t.created_at)
        parties_and_tickets.append((party, tickets_sorted))

    return {
        'user': user,
        'badges': badges,
        'orders': orders,
        'parties_and_tickets': parties_and_tickets,
    }


def _group_tickets_by_party(tickets):
    ticket_party_ids = {t.category.party_id for t in tickets}
    ticket_parties = party_service.get_parties(ticket_party_ids)
    ticket_parties_by_party_id = {p.id: p for p in ticket_parties}

    tickets_by_party = defaultdict(list)
    for ticket in tickets:
        party = ticket_parties_by_party_id[ticket.category.party_id]
        tickets_by_party[party].append(ticket)

    return tickets_by_party


@blueprint.route('/<uuid:user_id>/permissions')
@permission_required(UserPermission.view)
@templated
def view_permissions(user_id):
    """Show user's permissions."""
    user = _get_user_or_404(user_id)

    permissions_by_role = authorization_service \
        .get_permissions_by_roles_for_user_with_titles(user)

    return {
        'user': user,
        'permissions_by_role': permissions_by_role,
    }


@blueprint.route('/<uuid:user_id>/activity')
@permission_required(UserPermission.view)
@templated
def view_activity(user_id):
    """Show user's activity."""
    user = _get_user_or_404(user_id)

    newsletter_subscription_updates = newsletter_service \
        .get_subscription_updates_for_user(user.id)

    newsletter_subscription_updates.sort(key=lambda u: u.expressed_at,
                                         reverse=True)

    return {
        'user': user,
        'newsletter_subscription_updates': newsletter_subscription_updates,
    }


def _get_user_or_404(user_id):
    user = user_service.find_user(user_id)
    if user is None:
        abort(404)

    return user
