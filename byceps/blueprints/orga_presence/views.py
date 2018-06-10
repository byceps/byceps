"""
byceps.blueprints.orga_presence.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, datetime

from flask import abort

from ...services.orga_presence import service as orga_presence_service
from ...services.orga_presence.transfer.models import PartyTimeSlot, TimeSlot
from ...services.party import service as party_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import OrgaPresencePermission


blueprint = create_blueprint('orga_presence', __name__)


permission_registry.register_enum(OrgaPresencePermission)


@blueprint.route('/<party_id>')
@permission_required(OrgaPresencePermission.list)
@templated
def view(party_id):
    """List orga presence and task time slots for that party."""
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    party_time_slot = PartyTimeSlot.from_party(party)
    presences = orga_presence_service.get_presences(party.id)
    tasks = orga_presence_service.get_tasks(party.id)

    time_slots = [party_time_slot] + presences + tasks
    hour_ranges = list(orga_presence_service.get_hour_ranges(time_slots))

    days_and_hour_totals = list(orga_presence_service \
        .get_days_and_hour_totals(hour_ranges))

    return {
        'party': party,
        'days_and_hour_totals': days_and_hour_totals,
        'hour_ranges': hour_ranges,
        'party_time_slot': party_time_slot,
        'presences': presences,
        'tasks': tasks,
        'is_instant_contained_in_time_slot': is_instant_contained_in_time_slot,
    }


def is_instant_contained_in_time_slot(instant: datetime, time_slot: TimeSlot
                                     ) -> bool:
    return time_slot.range.contains(instant)
