"""
byceps.blueprints.api.v1.authn.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, jsonify, request

from byceps.blueprints.api.decorators import api_token_required
from byceps.services.authn.session import authn_session_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint


blueprint = create_blueprint('authn_api', __name__)


@blueprint.get('/logins')
@api_token_required
def get_logins_for_ip_address():
    """Return logins for an IP address."""
    ip_address = request.args.get('ip_address')
    if not ip_address:
        abort(400, "No value given for query parameter 'ip_address'.")

    occurred_at_and_user_ids = authn_session_service.find_logins_for_ip_address(
        ip_address
    )
    occurred_at_and_user_ids.sort()

    user_ids = {user_id for _, user_id in occurred_at_and_user_ids}
    users_by_id = user_service.get_users_indexed_by_id(user_ids)

    occurred_at_and_users = [
        (occurred_at, users_by_id[user_id])
        for occurred_at, user_id in occurred_at_and_user_ids
    ]

    logins = [
        {
            'occurred_at': occurred_at.isoformat(),
            'user_id': user.id,
            'user_screen_name': user.screen_name,
        }
        for occurred_at, user in occurred_at_and_users
    ]

    return jsonify(logins)
