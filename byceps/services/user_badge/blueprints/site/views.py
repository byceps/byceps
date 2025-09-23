"""
byceps.services.user_badge.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from byceps.services.orga_team import orga_team_service
from byceps.services.user import user_service
from byceps.services.user_badge import (
    user_badge_awarding_service,
    user_badge_service,
)
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated


blueprint = create_blueprint('user_badge', __name__)


@blueprint.get('/')
@templated
def index():
    """List all badges."""
    badges = user_badge_service.get_all_badges()

    return {
        'badges': badges,
    }


@blueprint.get('/<slug>')
@templated
def view(slug):
    """Show information about a badge."""
    badge = user_badge_service.find_badge_by_slug(slug)

    if badge is None:
        abort(404)

    awardings = user_badge_awarding_service.get_awardings_of_badge(badge.id)
    awardee_ids = {awarding.awardee_id for awarding in awardings}
    awardees = user_service.get_users(awardee_ids, include_avatars=True)
    awardees = list(sorted(awardees, key=lambda r: r.screen_name or ''))

    if not g.party:
        orga_ids = orga_team_service.select_orgas_for_party(
            awardee_ids, g.party.id
        )
    else:
        orga_ids = set()

    return {
        'badge': badge,
        'awardees': awardees,
        'orga_ids': orga_ids,
    }
