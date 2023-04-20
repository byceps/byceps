"""
byceps.blueprints.admin.attendance.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from byceps.services.brand import brand_service
from byceps.services.party import party_service
from byceps.services.ticketing import ticket_attendance_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required


blueprint = create_blueprint('attendance_admin', __name__)


@blueprint.get('/brands/<brand_id>')
@permission_required('admin.access')
@templated
def view_for_brand(brand_id):
    """Show most frequent attendees for parties of this brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    parties = party_service.get_parties_for_brand(brand.id)
    if parties:
        parties.sort(key=lambda party: party.starts_at, reverse=True)
        most_recent_party = parties[0]
    else:
        most_recent_party = None
    party_total = len(parties)

    top_attendees = _get_top_attendees(brand.id)

    return {
        'brand': brand,
        'party_total': party_total,
        'most_recent_party': most_recent_party,
        'top_attendees': top_attendees,
    }


def _get_top_attendees(brand_id):
    top_attendee_ids = ticket_attendance_service.get_top_attendees_for_brand(
        brand_id
    )

    top_attendees = _replace_user_ids_with_users(top_attendee_ids)

    # Sort by highest attendance count first, alphabetical screen name second.
    top_attendees.sort(key=lambda att: (-att[1], att[0].screen_name))

    return top_attendees


def _replace_user_ids_with_users(attendee_ids):
    users_by_id = _get_users_by_id(attendee_ids)

    return [
        (users_by_id[user_id], attendance_count)
        for user_id, attendance_count in attendee_ids
    ]


def _get_users_by_id(attendee_ids):
    user_ids = {user_id for user_id, attendance_count in attendee_ids}
    users = user_service.get_users(user_ids, include_avatars=False)
    return user_service.index_users_by_id(users)
