"""
byceps.blueprints.admin.ticketing.category.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from .....services.party import service as party_service
from .....services.ticketing import (
    category_service as ticketing_category_service,
)
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated
from .....util.views import permission_required

from ...ticketing.authorization import TicketingPermission


blueprint = create_blueprint('ticketing_category_admin', __name__)


@blueprint.route('/for_party/<party_id>')
@permission_required(TicketingPermission.administrate)
@templated
def index(party_id):
    """List ticket categories for that party."""
    party = _get_party_or_404(party_id)

    categories_with_ticket_counts = list(
        ticketing_category_service.get_categories_with_ticket_counts_for_party(
            party.id
        ).items()
    )

    return {
        'party': party,
        'categories_with_ticket_counts': categories_with_ticket_counts,
    }


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party
