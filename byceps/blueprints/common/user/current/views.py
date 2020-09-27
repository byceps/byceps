"""
byceps.blueprints.common.user.current.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, jsonify, Response

from .....config import get_app_mode
from .....util.framework.blueprint import create_blueprint


blueprint = create_blueprint('user_current', __name__)


@blueprint.route('/me.json')
def view_as_json():
    """Show selected attributes of the current user's profile as JSON."""
    if get_app_mode().is_admin():
        abort(404)

    user = g.current_user

    if not user.is_active:
        # Return empty response.
        return Response(status=403)

    return jsonify(
        {
            'id': user.id,
            'screen_name': user.screen_name,
            'avatar_url': user.avatar_url,
        }
    )
