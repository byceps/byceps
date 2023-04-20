"""
byceps.blueprints.admin.orga_presence.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime

from flask import abort, g, request
from flask_babel import to_utc

from byceps.services.orga_presence import orga_presence_service
from byceps.services.orga_presence.models import (
    PartyTimeSlot,
    PresenceTimeSlot,
    TimeSlot,
)
from byceps.services.party import party_service
from byceps.services.user.models.user import User
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, redirect_to, respond_no_content

from .forms import build_presence_create_form


blueprint = create_blueprint('orga_presence', __name__)


@blueprint.get('/<party_id>')
@permission_required('orga_presence.view')
@templated
def view(party_id):
    """List orga presence and task time slots for that party."""
    party = _get_party_or_404(party_id)

    party_time_slot = PartyTimeSlot.from_party(party)
    presences = orga_presence_service.get_presences(party.id)
    tasks = orga_presence_service.get_tasks(party.id)

    presences_by_orga = _group_presences_by_orga(presences)

    time_slots = [party_time_slot] + presences + tasks
    hour_ranges = list(orga_presence_service.get_hour_ranges(time_slots))

    days_and_hour_totals = list(
        orga_presence_service.get_days_and_hour_totals(hour_ranges)
    )

    current_user_presences = [
        presence for presence in presences if presence.orga.id == g.user.id
    ]

    return {
        'party': party,
        'days_and_hour_totals': days_and_hour_totals,
        'hour_ranges': hour_ranges,
        'party_time_slot': party_time_slot,
        'presences_by_orga': presences_by_orga,
        'tasks': tasks,
        'is_instant_contained_in_time_slots': is_instant_contained_in_time_slots,
        'current_user_presences': current_user_presences,
    }


def _group_presences_by_orga(
    presences: Iterable[PresenceTimeSlot],
) -> dict[User, set[PresenceTimeSlot]]:
    d = defaultdict(set)

    for presence in presences:
        d[presence.orga].add(presence)

    return d


def is_instant_contained_in_time_slots(
    instant: datetime, time_slots: Iterable[TimeSlot]
) -> bool:
    return any(time_slot.range.contains(instant) for time_slot in time_slots)


@blueprint.get('/<party_id>/presences/create')
@permission_required('orga_presence.update')
@templated
def create_form(party_id, erroneous_form=None):
    """Show form to create a presence for that party."""
    party = _get_party_or_404(party_id)

    party_time_slot = PartyTimeSlot.from_party(party)
    valid_range = party_time_slot.range

    CreateForm = build_presence_create_form(valid_range)
    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'party': party,
        'valid_range': valid_range,
        'form': form,
    }


@blueprint.post('/<party_id>/presences')
@permission_required('orga_presence.update')
def create(party_id):
    """Create a presence for that party."""
    party = _get_party_or_404(party_id)

    party_time_slot = PartyTimeSlot.from_party(party)

    CreateForm = build_presence_create_form(party_time_slot.range)
    form = CreateForm(request.form)

    if not form.validate():
        return create_form(party.id, form)

    starts_at_local = datetime.combine(form.starts_on.data, form.starts_at.data)
    starts_at_utc = to_utc(starts_at_local)
    ends_at_local = datetime.combine(form.ends_on.data, form.ends_at.data)
    ends_at_utc = to_utc(ends_at_local)

    orga_presence_service.create_presence(
        party.id,
        g.user.id,
        starts_at_utc,
        ends_at_utc,
    )

    return redirect_to('.view', party_id=party.id)


@blueprint.delete('/time_slots/<time_slot_id>')
@permission_required('orga_presence.update')
@respond_no_content
def time_slot_delete(time_slot_id):
    """Delete the time slot."""
    orga_presence_service.delete_time_slot(time_slot_id)


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party
