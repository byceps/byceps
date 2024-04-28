"""
byceps.blueprints.site.timetable.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict

from flask import abort, g

from byceps.services.timetable import timetable_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated


blueprint = create_blueprint('timetable', __name__)


@blueprint.get('')
@templated
def index():
    """Show timetable for current party."""
    timetable = _get_timetable_for_party_or_404(g.party_id)

    items_grouped_by_day = _group_items_by_day(timetable)

    return {
        'items_grouped_by_day': items_grouped_by_day,
    }


def _group_items_by_day(timetable):
    items_grouped_by_day = defaultdict(list)

    for item in timetable.items:
        if not item.hidden:
            items_grouped_by_day[item.scheduled_at.date()].append(item)

    return dict(items_grouped_by_day)


# -------------------------------------------------------------------- #


def _get_timetable_for_party_or_404(party_id):
    timetable = timetable_service.find_timetable_for_party(party_id)

    if timetable is None:
        abort(404)

    return timetable
