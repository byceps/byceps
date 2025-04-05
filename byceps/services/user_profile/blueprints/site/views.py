"""
byceps.services.user_profile.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from operator import attrgetter

from flask import abort, g

from byceps.services.orga_team import orga_team_service
from byceps.services.ticketing import ticket_attendance_service, ticket_service
from byceps.services.user import user_service
from byceps.services.user_badge import user_badge_awarding_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated


blueprint = create_blueprint('user_profile', __name__)


@blueprint.get('/<uuid:user_id>')
@templated
def view(user_id):
    """Show a user's profile."""
    user = user_service.find_active_user(user_id, include_avatar=True)
    if user is None:
        abort(404)

    badges_with_awarding_quantity = (
        user_badge_awarding_service.get_badges_awarded_to_user(user.id)
    )

    orga_teams = orga_team_service.get_orga_teams_for_user_and_party(
        user.id, g.party_id
    )

    _current_party_tickets = ticket_service.get_tickets_used_by_user(
        user.id, g.party_id
    )
    current_party_tickets = [t for t in _current_party_tickets if not t.revoked]

    attended_parties = ticket_attendance_service.get_attended_parties(user.id)
    attended_parties = [party for party in attended_parties if not party.hidden]
    attended_parties.sort(key=attrgetter('starts_at'), reverse=True)

    return {
        'user': user,
        'badges_with_awarding_quantity': badges_with_awarding_quantity,
        'orga_teams': orga_teams,
        'current_party_tickets': current_party_tickets,
        'attended_parties': attended_parties,
    }
