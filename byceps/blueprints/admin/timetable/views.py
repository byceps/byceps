"""
byceps.blueprints.admin.timetable.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict

from flask import abort

from byceps.services.party import party_service
from byceps.services.timetable import timetable_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required


blueprint = create_blueprint('timetable_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('timetable.update')
@templated
def view(party_id):
    """Show timetable for party."""
    party = _get_party_or_404(party_id)

    timetable = _get_timetable_for_party_or_404(party.id)

    items_grouped_by_day = _group_items_by_day(timetable)

    return {
        'party': party,
        'items_grouped_by_day': items_grouped_by_day,
    }


def _group_items_by_day(timetable):
    items_grouped_by_day = defaultdict(list)

    for item in timetable.items:
        items_grouped_by_day[item.scheduled_at.date()].append(item)

    return dict(items_grouped_by_day)


# -------------------------------------------------------------------- #


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_timetable_for_party_or_404(party_id):
    timetable = timetable_service.find_timetable_for_party(party_id)

    if timetable is None:
        abort(404)

    return timetable
