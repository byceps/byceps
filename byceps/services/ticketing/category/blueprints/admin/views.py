"""
byceps.services.ticketing.category.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from byceps.services.party import party_service
from byceps.services.ticketing import ticket_category_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, redirect_to

from .forms import CreateOrUpdateForm


blueprint = create_blueprint('ticketing_category_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('ticketing.administrate')
@templated
def index(party_id):
    """List ticket categories for that party."""
    party = _get_party_or_404(party_id)

    categories_with_ticket_counts = list(
        ticket_category_service.get_categories_with_ticket_counts_for_party(
            party.id
        ).items()
    )

    return {
        'party': party,
        'categories_with_ticket_counts': categories_with_ticket_counts,
    }


@blueprint.get('/for_party/<party_id>/create')
@permission_required('ticketing.administrate')
@templated
def create_form(party_id, erroneous_form=None):
    """Show form to create a ticket category."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else CreateOrUpdateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/for_party/<party_id>')
@permission_required('ticketing.administrate')
def create(party_id):
    """Create a ticket category."""
    party = _get_party_or_404(party_id)

    form = CreateOrUpdateForm(request.form)
    if not form.validate():
        return create_form(party.id, form)

    title = form.title.data.strip()

    category = ticket_category_service.create_category(party.id, title)

    flash_success(
        gettext('Category "%(title)s" has been created.', title=category.title)
    )

    return redirect_to('.index', party_id=party.id)


@blueprint.get('/categories/<uuid:category_id>/update')
@permission_required('ticketing.administrate')
@templated
def update_form(category_id, erroneous_form=None):
    """Show form to update the category."""
    category = _get_category_or_404(category_id)

    party = party_service.find_party(category.party_id)

    form = (
        erroneous_form if erroneous_form else CreateOrUpdateForm(obj=category)
    )

    return {
        'party': party,
        'category': category,
        'form': form,
    }


@blueprint.post('/categories/<uuid:category_id>')
@permission_required('ticketing.administrate')
def update(category_id):
    """Update the category."""
    category = _get_category_or_404(category_id)

    form = CreateOrUpdateForm(request.form)
    if not form.validate():
        return update_form(category.id, form)

    title = form.title.data.strip()

    category = ticket_category_service.update_category(category.id, title)

    flash_success(
        gettext('Category "%(title)s" has been updated.', title=category.title)
    )

    return redirect_to('.index', party_id=category.party_id)


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_category_or_404(category_id):
    category = ticket_category_service.find_category(category_id)

    if category is None:
        abort(404)

    return category
