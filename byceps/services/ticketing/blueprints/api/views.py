"""
byceps.services.ticketing.blueprints.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, jsonify

from byceps.services.party import party_service
from byceps.services.party.models import Party, PartyID
from byceps.services.ticketing import ticket_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import api_token_required


blueprint = create_blueprint('ticketing_api', __name__)


@blueprint.get('/sale_stats/<party_id>')
@api_token_required
def get_sale_stats(party_id):
    """Return the number of maximum and sold tickets, respectively, for
    that party.
    """
    party = _get_party_or_404(party_id)

    sale_stats = ticket_service.get_ticket_sale_stats(party)

    return jsonify(
        {
            'tickets_max': sale_stats.tickets_max,
            'tickets_sold': sale_stats.tickets_sold,
        }
    )


def _get_party_or_404(party_id: PartyID) -> Party:
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party
