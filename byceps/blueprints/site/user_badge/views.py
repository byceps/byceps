"""
byceps.blueprints.site.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ....services.user import service as user_service
from ....services.user_badge import awarding_service, badge_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated


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

    awardings = awarding_service.get_awardings_of_badge(badge.id)
    recipient_ids = [awarding.user_id for awarding in awardings]
    recipients = user_service.find_users(
        recipient_ids,
        include_avatars=True,
        include_orga_flags_for_party_id=g.party_id,
    )

    return {
        'badge': badge,
        'recipients': recipients,
    }
