"""
byceps.blueprints.api.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.user import service as user_service
from ....services.user_badge import (
    command_service as badge_command_service,
    service as badge_service,
)
from ....util.framework.blueprint import create_blueprint
from ....util.views import respond_no_content

from ..decorators import api_token_required

from ...user_badge import signals


blueprint = create_blueprint('api_user_badge', __name__)


@blueprint.route('/<uuid:badge_id>/awardings', methods=['POST'])
@api_token_required
@respond_no_content
def award_badge_to_user(badge_id):
    """Award the badge to a user."""
    badge = _get_badge_or_404(badge_id)

    user = _get_user_or_400()
    initiator = _get_initiator_or_400()

    _, event = badge_command_service.award_badge_to_user(
        badge.id, user.id, initiator_id=initiator.id
    )

    signals.user_badge_awarded.send(None, event=event)


def _get_badge_or_404(badge_id):
    badge = badge_service.find_badge(badge_id)

    if badge is None:
        abort(404)

    return badge


def _get_user_or_400():
    user_id = request.form['user_id'].strip()
    if not user_id:
        abort(400, 'User ID missing')

    user = user_service.find_user(user_id)
    if not user:
        abort(400, 'User ID unknown')

    return user


def _get_initiator_or_400():
    initiator_id = request.form['initiator_id'].strip()
    if not initiator_id:
        abort(400, 'Initiator ID missing')

    initiator = user_service.find_user(initiator_id)
    if not initiator:
        abort(400, 'Initiator ID unknown')

    return initiator
