"""
byceps.blueprints.site.party_history.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from byceps.blueprints.site.site.navigation import subnavigation_for_view
from byceps.services.party import party_service
from byceps.services.ticketing import ticket_attendance_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated


blueprint = create_blueprint('party_history', __name__)


@blueprint.get('')
@templated
@subnavigation_for_view('party_history')
def index():
    """List archived parties."""
    parties = party_service.get_archived_parties_for_brand(g.brand_id)
    parties = [p for p in parties if not p.canceled]

    return {
        'parties': parties,
    }


@blueprint.get('/<party_id>')
@templated
@subnavigation_for_view('party_history')
def view(party_id):
    """Show archived party."""
    party = party_service.find_party(party_id)
    if (
        (party is None)
        or (party.brand_id != g.brand_id)
        or not party.archived
        or party.canceled
    ):
        abort(404)

    attendee_ids = ticket_attendance_service.get_attendee_ids_for_party(
        party_id
    )
    attendees = user_service.get_users(attendee_ids, include_avatars=True)
    attendees = [attendee for attendee in attendees if not attendee.deleted]

    return {
        'party': party,
        'attendees': attendees,
    }
