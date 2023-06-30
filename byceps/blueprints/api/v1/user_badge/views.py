"""
byceps.blueprints.api.v1.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from pydantic import ValidationError

from byceps.blueprints.api.decorators import api_token_required
from byceps.services.user import user_service
from byceps.services.user_badge import (
    user_badge_awarding_service,
    user_badge_service,
)
from byceps.signals import user_badge as user_badge_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import respond_no_content

from .models import AwardBadgeToUserRequest


blueprint = create_blueprint('user_badge_api', __name__)


@blueprint.post('/awardings')
@api_token_required
@respond_no_content
def award_badge_to_user():
    """Award the badge to a user."""
    if not request.is_json:
        abort(415)

    try:
        req = AwardBadgeToUserRequest.parse_obj(request.get_json())
    except ValidationError as e:
        abort(400, e.json())

    badge = user_badge_service.find_badge_by_slug(req.badge_slug)
    if not badge:
        abort(400, 'Badge slug unknown')

    awardee = user_service.find_user(req.awardee_id)
    if not awardee:
        abort(400, 'Awardee ID unknown')

    initiator = user_service.find_user(req.initiator_id)
    if not initiator:
        abort(400, 'Initiator ID unknown')

    _, event = user_badge_awarding_service.award_badge_to_user(
        badge.id, awardee.id, initiator_id=initiator.id
    )

    user_badge_signals.user_badge_awarded.send(None, event=event)
