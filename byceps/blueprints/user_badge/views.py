"""
byceps.blueprints.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ...services.orga_team import service as orga_team_service
from ...services.user import service as user_service
from ...services.user_badge import service as badge_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated


blueprint = create_blueprint('user_badge', __name__)


@blueprint.route('/')
@templated
def index():
    """List all badges."""
    badges = badge_service.get_all_badges()

    return {
        'badges': badges,
    }


@blueprint.route('/<slug>')
@templated
def view(slug):
    """Show information about a badge."""
    badge = badge_service.find_badge_by_slug(slug)

    if badge is None:
        abort(404)

    awardings = badge_service.get_awardings_of_badge(badge.id)
    recipient_ids = [awarding.user_id for awarding in awardings]
    recipients = user_service.find_users(recipient_ids)

    # Find out which user is an organizer of this party.
    orga_ids = orga_team_service.select_orgas_for_party(
        recipient_ids, g.party_id)

    # Update organizer flags.
    recipients = {r._replace(is_orga=(r.id in orga_ids)) for r in recipients}

    return {
        'badge': badge,
        'recipients': recipients,
    }
