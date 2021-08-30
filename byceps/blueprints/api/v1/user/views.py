"""
byceps.blueprints.api.v1.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, jsonify, request
from marshmallow import ValidationError

from .....services.user import (
    email_address_verification_service,
    service as user_service,
)
from .....signals import user as user_signals
from .....util.framework.blueprint import create_blueprint
from .....util.views import create_empty_json_response
from .....util.views import respond_no_content

from ...decorators import api_token_required

from .schemas import InvalidateEmailAddressRequest


blueprint = create_blueprint('user', __name__)


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
    schema = InvalidateEmailAddressRequest()
    request_data = request.get_json()

    try:
        req = schema.load(request_data)
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    user = user_service.find_user_by_email_address(req['email_address'])

    if user is None:
        abort(404, 'Unknown email address')

    event = email_address_verification_service.invalidate_email_address(
        user.id, req['reason']
    )

    user_signals.email_address_invalidated.send(None, event=event)
