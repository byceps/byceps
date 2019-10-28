"""
byceps.blueprints.api.attendance.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.party import service as party_service
from ....services.ticketing import attendance_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.views import respond_no_content

from ..decorators import api_token_required


blueprint = create_blueprint('api_attendance', __name__)


@blueprint.route('/archived_attendances', methods=['POST'])
@api_token_required
@respond_no_content
def create_archived_attendance():
    """Create an archived attendance of the user at the party."""
    user = _get_user_or_400()
    party = _get_party_or_400()

    attendance_service.create_archived_attendance(user.id, party.id)


def _get_user_or_400():
    user_id = request.form['user_id']
    if not user_id:
        abort(400, 'User ID missing')

    user = user_service.find_user(user_id)
    if not user:
        abort(400, 'User ID unknown')

    return user


def _get_party_or_400():
    party_id = request.form['party_id']
    if party_id is None:
        abort(400, 'Party ID missing')

    party = party_service.find_party(party_id)
    if not party:
        abort(400, 'Party ID unknown')

    return party
