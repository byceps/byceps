"""
byceps.blueprints.site.timetable.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from itertools import chain

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

    return {
        'timetable': timetable,
    }


# -------------------------------------------------------------------- #


def _get_timetable_for_party_or_404(party_id):
    timetable = timetable_service.find_timetable_grouped_by_day_for_party(
        party_id, include_hidden_items=False
    )

    if (
        (timetable is None)
        or timetable.hidden
        or _has_only_hidden_items(timetable)
    ):
        abort(404)

    return timetable


def _has_only_hidden_items(timetable):
    items = chain.from_iterable(day_items for _, day_items in timetable.items)
    return all(item.hidden for item in items)
