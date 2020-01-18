"""
byceps.blueprints.api.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import jsonify

from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.views import create_empty_json_response


blueprint = create_blueprint('api_user', __name__)


@blueprint.route('/<uuid:user_id>/profile')
def get_profile(user_id):
    """Return (part of) user's profile as JSON."""
    user = user_service.find_active_user(user_id, include_avatar=True)

    if user is None:
        return create_empty_json_response(404)

    return jsonify({
        'id': user.id,
        'screen_name': user.screen_name,
        'avatar_url': user.avatar_url,
    })
