"""
byceps.blueprints.site.timetable.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

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
        party_id
    )

    if timetable is None:
        abort(404)

    return timetable
