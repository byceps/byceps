"""
byceps.blueprints.api.v1.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request
from marshmallow import ValidationError

from .....services.user import service as user_service
from .....services.user_badge import (
    command_service as badge_command_service,
    service as badge_service,
)
from .....util.framework.blueprint import create_blueprint
from .....util.views import respond_no_content

from ...decorators import api_token_required

from ....user_badge import signals

from .schemas import AwardBadgeToUserRequest


blueprint = create_blueprint('api_v1_user_badge', __name__)


@blueprint.route('/awardings', methods=['POST'])
@api_token_required
@respond_no_content
def award_badge_to_user():
    """Award the badge to a user."""
    if not request.is_json:
        abort(415)

    schema = AwardBadgeToUserRequest()
    try:
        req = schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    badge = badge_service.find_badge_by_slug(req['badge_slug']).value_or(None)
    if not badge:
        abort(400, 'Badge slug unknown')

    user = user_service.find_user(req['user_id'])
    if not user:
        abort(400, 'User ID unknown')

    initiator = user_service.find_user(req['initiator_id'])
    if not initiator:
        abort(400, 'Initiator ID unknown')

    _, event = badge_command_service.award_badge_to_user(
        badge.id, user.id, initiator_id=initiator.id
    )

    signals.user_badge_awarded.send(None, event=event)
