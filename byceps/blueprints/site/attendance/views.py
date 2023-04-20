"""
byceps.blueprints.site.attendance.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request

from byceps.blueprints.site.site.navigation import subnavigation_for_view
from byceps.services.attendance import attendance_service
from byceps.services.orga_team import orga_team_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated


blueprint = create_blueprint('attendance', __name__)


@blueprint.get('/attendees', defaults={'page': 1})
@blueprint.get('/attendees/pages/<int:page>')
@templated
@subnavigation_for_view('attendees')
def attendees(page):
    """List all attendees of the current party."""
    per_page = request.args.get('per_page', type=int, default=30)
    search_term = request.args.get('search_term', default='').strip()

    if g.party_id is None:
        # No party is configured for the current site.
        abort(404)

    attendees = attendance_service.get_attendees_paginated(
        g.party_id, page, per_page, search_term=search_term
    )

    attendee_ids = {attendee.user.id for attendee in attendees.items}
    orga_ids = orga_team_service.select_orgas_for_party(
        attendee_ids, g.party_id
    )

    return {
        'per_page': per_page,
        'search_term': search_term,
        'attendees': attendees,
        'orga_ids': orga_ids,
    }
