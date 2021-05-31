"""
byceps.blueprints.site.party_history.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from ....services.party import service as party_service
from ....services.ticketing import attendance_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated


blueprint = create_blueprint('party_archive', __name__)


@blueprint.get('')
@templated
def index():
    """List archived parties."""
    archived_parties = party_service.get_archived_parties_for_brand(g.brand_id)

    return {
        'parties': archived_parties,
    }


@blueprint.get('/<party_id>')
@templated
def view(party_id):
    """Show archived party."""
    party = party_service.find_party(party_id)
    if (party is None) or (party.brand_id != g.brand_id) or not party.archived:
        abort(404)

    attendees = attendance_service.get_attendees_for_party(party_id)

    return {
        'party': party,
        'attendees': attendees,
    }
