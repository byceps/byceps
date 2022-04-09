"""
byceps.blueprints.api.v1.attendance.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from marshmallow import ValidationError

from .....services.party import service as party_service
from .....services.ticketing import attendance_service
from .....services.user import service as user_service
from .....util.framework.blueprint import create_blueprint
from .....util.views import respond_no_content

from ...decorators import api_token_required

from .schemas import CreateArchivedAttendanceRequest


blueprint = create_blueprint('attendance_api', __name__)


@blueprint.post('/archived_attendances')
@api_token_required
@respond_no_content
def create_archived_attendance():
    """Create an archived attendance of the user at the party."""
    if not request.is_json:
        abort(415)

    schema = CreateArchivedAttendanceRequest()
    try:
        req = schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    user = user_service.find_user(req['user_id'])
    if not user:
        abort(400, 'User ID unknown')

    party = party_service.find_party(req['party_id'])
    if not party:
        abort(400, 'Party ID unknown')

    attendance_service.create_archived_attendance(user.id, party.id)
