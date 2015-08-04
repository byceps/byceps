# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_presence.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import groupby

from arrow import Arrow

from ...database import db
from ...util.datetime import DateTimeRange
from ...util.framework import create_blueprint
from ...util.iterables import pairwise
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party.models import Party

from .authorization import OrgaPresencePermission
from .models import Presence, Task


blueprint = create_blueprint('orga_presence', __name__)


permission_registry.register_enum(OrgaPresencePermission)


@blueprint.route('/')
@permission_required(OrgaPresencePermission.list)
@templated
def index():
    """List parties to choose from."""
    parties = Party.query.all()

    return {'parties': parties}


@blueprint.route('/<party_id>')
@permission_required(OrgaPresencePermission.list)
@templated
def view(party_id):
    """List orga presence and task time slots for that party."""
    party = Party.query.get_or_404(party_id)

    presences = Presence.query \
        .for_party(party) \
        .options(db.joinedload('orga')) \
        .all()
    tasks = Task.query.for_party(party).all()

    time_slots = [party] + tasks
    min_starts_at = find_earliest_time_slot_start(time_slots)
    max_ends_at = find_latest_time_slot_end(time_slots)

    hour_starts_arrow = Arrow.range('hour', min_starts_at, max_ends_at)
    hour_starts = [hour_start.datetime.replace(tzinfo=None)
                   for hour_start in hour_starts_arrow]

    hour_ranges = list(map(DateTimeRange._make, pairwise(hour_starts)))

    days = [(day, len(list(hour_starts))) for day, hour_starts
                  in groupby(hour_starts, key=lambda hour: hour.date())]

    return {
        'party': party,
        'days': days,
        'hour_ranges': hour_ranges,
        'presences': presences,
        'tasks': tasks,
    }


def find_earliest_time_slot_start(time_slots):
    return min(time_slot.range.start for time_slot in time_slots)


def find_latest_time_slot_end(time_slots):
    return max(time_slot.range.end for time_slot in time_slots)
