"""
byceps.services.user.blueprints.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, jsonify, request
from pydantic import ValidationError

from byceps.services.user import (
    signals as user_signals,
    user_email_address_service,
    user_service,
)
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import (
    api_token_required,
    create_empty_json_response,
    respond_no_content,
)

from .models import InvalidateEmailAddressRequest


blueprint = create_blueprint('user_api', __name__)


@blueprint.get('/<uuid:user_id>/profile')
def get_profile(user_id):
    """Return (part of) user's profile as JSON."""
    user = user_service.find_active_user(user_id, include_avatar=True)

    if user is None:
        return create_empty_json_response(404)

    return jsonify(
        {
            'id': user.id,
            'screen_name': user.screen_name,
            'avatar_url': user.avatar_url,
        }
    )


@blueprint.post('/invalidate_email_address')
@api_token_required
@respond_no_content
def invalidate_email_address():
    """Invalidate the email address."""
    try:
        req = InvalidateEmailAddressRequest.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, e.json())

    user = user_service.find_user_by_email_address(req.email_address)

    if user is None:
        abort(400, 'Unknown email address')

    invalidation_result = user_email_address_service.invalidate_email_address(
        user, req.reason
    )

    if invalidation_result.is_err():
        abort(400, invalidation_result.unwrap_err())

    event = invalidation_result.unwrap()

    user_signals.email_address_invalidated.send(None, event=event)
