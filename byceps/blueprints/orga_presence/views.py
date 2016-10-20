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

from ...services.orga_presence import service as orga_presence_service
from ...services.party import service as party_service
from ...util.datetime.range import create_adjacent_ranges
from ...util.framework import create_blueprint
from ...util.templating import templated

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

    presences = orga_presence_service.get_presences(party.id)
    tasks = orga_presence_service.get_tasks(party.id)

    time_slot_ranges = list(_get_time_slot_ranges(party, tasks))

    hour_starts = list(_get_hour_starts(time_slot_ranges))

    hour_ranges = list(create_adjacent_ranges(hour_starts))

    days_and_hour_totals = _get_days_and_hour_totals(hour_starts)

    return {
        'party': party,
        'days_and_hour_totals': days_and_hour_totals,
        'hour_ranges': hour_ranges,
        'presences': presences,
        'tasks': tasks,
    }


def _get_time_slot_ranges(party, tasks):
    time_slots = [party] + tasks
    for time_slot in time_slots:
        yield time_slot.range


def _get_hour_starts(dt_ranges):
    min_starts_at = _find_earliest_start(dt_ranges)
    max_ends_at = _find_latest_end(dt_ranges)

    hour_starts_arrow = Arrow.range('hour', min_starts_at, max_ends_at)

    return _to_datetimes_without_tzinfo(hour_starts_arrow)


def _find_earliest_start(dt_ranges):
    return min(dt_range.start for dt_range in dt_ranges)


def _find_latest_end(dt_ranges):
    return max(dt_range.end for dt_range in dt_ranges)


def _to_datetimes_without_tzinfo(arrow_datetimes):
    for arrow_datetime in arrow_datetimes:
        yield arrow_datetime.datetime.replace(tzinfo=None)


def _get_days_and_hour_totals(hour_starts):
    def get_date(dt):
        return dt.date()

    for day, hour_starts_for_day in groupby(hour_starts, key=get_date):
        hour_total = len(list(hour_starts_for_day))
        yield day, hour_total
