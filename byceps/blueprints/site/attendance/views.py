"""
byceps.blueprints.site.attendance.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request

from ....services.attendance import service as attendance_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated


blueprint = create_blueprint('attendance', __name__)


@blueprint.route('/attendees', defaults={'page': 1})
@blueprint.route('/attendees/pages/<int:page>')
@templated
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

    return {
        'search_term': search_term,
        'attendees': attendees,
    }
