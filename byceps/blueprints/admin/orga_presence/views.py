"""
byceps.blueprints.admin.orga_presence.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from typing import Iterable

from flask import abort

from ....services.orga_presence import service as orga_presence_service
from ....services.orga_presence.transfer.models import (
    PartyTimeSlot,
    PresenceTimeSlot,
    TimeSlot,
)
from ....services.party import service as party_service
from ....services.user.transfer.models import User
from ....util.authorization import register_permission_enum
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import permission_required

from .authorization import OrgaPresencePermission


blueprint = create_blueprint('orga_presence', __name__)


register_permission_enum(OrgaPresencePermission)


@blueprint.route('/<party_id>')
@permission_required(OrgaPresencePermission.view)
@templated
def view(party_id):
    """List orga presence and task time slots for that party."""
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    party_time_slot = PartyTimeSlot.from_party(party)
    presences = orga_presence_service.get_presences(party.id)
    tasks = orga_presence_service.get_tasks(party.id)

    presences_by_orga = _group_presences_by_orga(presences)

    time_slots = [party_time_slot] + presences + tasks
    hour_ranges = list(orga_presence_service.get_hour_ranges(time_slots))

    days_and_hour_totals = list(
        orga_presence_service.get_days_and_hour_totals(hour_ranges)
    )

    return {
        'party': party,
        'days_and_hour_totals': days_and_hour_totals,
        'hour_ranges': hour_ranges,
        'party_time_slot': party_time_slot,
        'presences_by_orga': presences_by_orga,
        'tasks': tasks,
        'is_instant_contained_in_time_slots': is_instant_contained_in_time_slots,
    }


def _group_presences_by_orga(
    presences: Iterable[PresenceTimeSlot],
) -> dict[User, PresenceTimeSlot]:
    d = defaultdict(set)

    for presence in presences:
        d[presence.orga].add(presence)

    return d


def is_instant_contained_in_time_slots(
    instant: datetime, time_slots: Iterable[TimeSlot]
) -> bool:
    return any(time_slot.range.contains(instant) for time_slot in time_slots)
