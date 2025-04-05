"""
byceps.services.attendance.blueprints.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from pydantic import ValidationError

from byceps.blueprints.api.decorators import api_token_required
from byceps.services.party import party_service
from byceps.services.ticketing import ticket_attendance_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import respond_no_content

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

    user = user_service.find_user(req.user_id)
    if not user:
        abort(400, 'User ID unknown')

    party = party_service.find_party(req.party_id)
    if not party:
        abort(400, 'Party ID unknown')

    ticket_attendance_service.create_archived_attendance(user.id, party.id)
