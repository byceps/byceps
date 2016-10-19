# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_presence.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import groupby

from arrow import Arrow
from flask import abort

from ...services.party import service as party_service
from ...util.datetime import DateTimeRange
from ...util.framework import create_blueprint
from ...util.iterables import pairwise
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import OrgaPresencePermission
from . import service


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

    presences = service.get_presences(party.id)
    tasks = service.get_tasks(party.id)

    time_slots = [party] + tasks

    hour_starts = list(_get_hour_starts(time_slots))

    hour_ranges = list(_to_hour_ranges(hour_starts))

    days_and_hour_totals = _get_days_and_hour_totals(hour_starts)

    return {
        'party': party,
        'days_and_hour_totals': days_and_hour_totals,
        'hour_ranges': hour_ranges,
        'presences': presences,
        'tasks': tasks,
    }


def _get_hour_starts(time_slots):
    min_starts_at = _find_earliest_time_slot_start(time_slots)
    max_ends_at = _find_latest_time_slot_end(time_slots)

    hour_starts_arrow = Arrow.range('hour', min_starts_at, max_ends_at)

    return _to_datetimes_without_tzinfo(hour_starts_arrow)


def _find_earliest_time_slot_start(time_slots):
    return min(time_slot.range.start for time_slot in time_slots)


def _find_latest_time_slot_end(time_slots):
    return max(time_slot.range.end for time_slot in time_slots)


def _to_datetimes_without_tzinfo(arrow_datetimes):
    for arrow_datetime in arrow_datetimes:
        yield arrow_datetime.datetime.replace(tzinfo=None)


def _to_hour_ranges(hour_starts):
    for pair in pairwise(hour_starts):
        yield DateTimeRange._make(pair)


def _get_days_and_hour_totals(hour_starts):
    def get_date(dt):
        return dt.date()

    for day, hour_starts_for_day in groupby(hour_starts, key=get_date):
        hour_total = len(list(hour_starts_for_day))
        yield day, hour_total
