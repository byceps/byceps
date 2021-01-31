"""
byceps.blueprints.admin.ticketing.category.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from .....services.party import service as party_service
from .....services.ticketing import (
    category_service as ticketing_category_service,
)
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to

from ...ticketing.authorization import TicketingPermission

from .forms import CreateForm


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


@blueprint.route('/for_party/<party_id>/create')
@permission_required(TicketingPermission.administrate)
@templated
def create_form(party_id, erroneous_form=None):
    """Show form to create a ticket category."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/for_party/<party_id>', methods=['POST'])
@permission_required(TicketingPermission.administrate)
def create(party_id):
    """Create a ticket category."""
    party = _get_party_or_404(party_id)

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(party.id, form)

    title = form.title.data.strip()

    category = ticketing_category_service.create_category(party.id, title)

    flash_success(
        gettext(
            'Ticket category "%(title)s" has been created.',
            title=category.title,
        )
    )

    return redirect_to('.index', party_id=party.id)


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party
