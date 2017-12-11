"""
byceps.blueprints.ticketing.checkin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from ....services.party import service as party_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry
from ...ticketing_admin.authorization import TicketingPermission


blueprint = create_blueprint('ticketing_checkin', __name__)


@blueprint.route('/for_party/<party_id>')
@permission_required(TicketingPermission.checkin)
@templated
def index(party_id):
    """Provide form to find tickets, then check them in."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    return {
        'party': party,
        'search_term': '',
    }
