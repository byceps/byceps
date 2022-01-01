"""
byceps.blueprints.site.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from ....services.orga_team import service as orga_team_service
from ....services.user import service as user_service
from ....services.user_badge import awarding_service, badge_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated


blueprint = create_blueprint('user_badge', __name__)


@blueprint.get('/')
@templated
def index():
    """List all badges."""
    badges = badge_service.get_all_badges()

    return {
        'badges': badges,
    }


@blueprint.get('/<slug>')
@templated
def view(slug):
    """Show information about a badge."""
    badge = badge_service.find_badge_by_slug(slug)

    if badge is None:
        abort(404)

    awardings = awarding_service.get_awardings_of_badge(badge.id)
    recipient_ids = {awarding.user_id for awarding in awardings}
    recipients = user_service.get_users(recipient_ids, include_avatars=True)

    if g.party_id is not None:
        orga_ids = orga_team_service.select_orgas_for_party(
            recipient_ids, g.party_id
        )
    else:
        orga_ids = set()

    return {
        'badge': badge,
        'recipients': recipients,
        'orga_ids': orga_ids,
    }
