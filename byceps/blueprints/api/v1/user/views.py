"""
byceps.blueprints.api.v1.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, jsonify, request
from pydantic import ValidationError

from byceps.blueprints.api.decorators import api_token_required
from byceps.services.user import user_email_address_service, user_service
from byceps.signals import user as user_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import create_empty_json_response, respond_no_content

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
        abort(404, 'Unknown email address')

    event = user_email_address_service.invalidate_email_address(
        user.id, req.reason
    )

    user_signals.email_address_invalidated.send(None, event=event)
