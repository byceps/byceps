"""
byceps.services.attendance.blueprints.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from pydantic import ValidationError

from byceps.services.party import party_service
from byceps.services.party.models import PartyID
from byceps.services.ticketing import ticket_attendance_service
from byceps.services.user import user_service
from byceps.services.user.models.user import UserID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import api_token_required, respond_no_content

from .models import CreateArchivedAttendanceRequest


blueprint = create_blueprint('attendance_api', __name__)


@blueprint.post('/archived_attendances')
@api_token_required
@respond_no_content
def create_archived_attendance():
    """Create an archived attendance of the user at the party."""
    if not request.is_json:
        abort(415)

    try:
        req = CreateArchivedAttendanceRequest.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, e.json())

    user_id = UserID(req.user_id)
    user = user_service.find_user(user_id)
    if not user:
        abort(400, 'User ID unknown')

    party_id = PartyID(req.party_id)
    party = party_service.find_party(party_id)
    if not party:
        abort(400, 'Party ID unknown')

    ticket_attendance_service.create_archived_attendance(user.id, party.id)
