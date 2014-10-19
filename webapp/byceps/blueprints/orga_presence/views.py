# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_presence.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import timedelta
from itertools import groupby

from arrow import Arrow

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

    party_span_starts_at = party.starts_at - timedelta(days=2)
    party_span_ends_at = party.ends_at + timedelta(days=2)
    hour_starts_arrow = Arrow.range('hour', party_span_starts_at, party_span_ends_at)
    hour_starts = [hour_start.datetime.replace(tzinfo=None)
                   for hour_start in hour_starts_arrow]

    hour_ranges = list(map(DateTimeRange._make, pairwise(hour_starts)))

    days = [(day, len(list(hour_starts))) for day, hour_starts
                  in groupby(hour_starts, key=lambda hour: hour.date())]

    presences = Presence.query.for_party(party).all()
    tasks = Task.query.for_party(party).all()

    return {
        'party': party,
        'days': days,
        'hour_ranges': hour_ranges,
        'presences': presences,
        'tasks': tasks,
    }
