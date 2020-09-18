"""
byceps.blueprints.admin.tourney.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.party import service as party_service
from ....services.tourney import category_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to, respond_no_content

from ...common.authorization.decorators import permission_required
from ...common.authorization.registry import permission_registry

from .authorization import TourneyCategoryPermission
from .forms import TourneyCategoryCreateForm, TourneyCategoryUpdateForm


blueprint = create_blueprint('tourney_admin', __name__)


permission_registry.register_enum(TourneyCategoryPermission)


@blueprint.route('/parties/<party_id>/categories')
@permission_required(TourneyCategoryPermission.view)
@templated
def category_index_for_party(party_id):
    """List tourney categories for that party."""
    party = _get_party_or_404(party_id)

    categories = category_service.get_categories_for_party(party.id)

    return {
        'party': party,
        'categories': categories,
    }


@blueprint.route('/parties/<party_id>/categories/create')
@permission_required(TourneyCategoryPermission.create)
@templated
def category_create_form(party_id, erroneous_form=None):
    """Show form to create a category."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else TourneyCategoryCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/parties/<party_id>/categories', methods=['POST'])
@permission_required(TourneyCategoryPermission.create)
def category_create(party_id):
    """Create a category."""
    party = _get_party_or_404(party_id)

    form = TourneyCategoryCreateForm(request.form)
    if not form.validate():
        return category_create_form(party_id, form)

    title = form.title.data.strip()

    category = category_service.create_category(party.id, title)

    flash_success(f'Die Kategorie "{category.title}" wurde angelegt.')
    return redirect_to('.category_index_for_party', party_id=category.party_id)


@blueprint.route('/categories/<uuid:category_id>/update')
@permission_required(TourneyCategoryPermission.update)
@templated
def category_update_form(category_id, erroneous_form=None):
    """Show form to update a category."""
    category = _get_category_or_404(category_id)

    party = party_service.get_party(category.party_id)

    form = (
        erroneous_form
        if erroneous_form
        else TourneyCategoryUpdateForm(obj=category)
    )

    return {
        'category': category,
        'party': party,
        'form': form,
    }


@blueprint.route('/categories/<uuid:category_id>', methods=['POST'])
@permission_required(TourneyCategoryPermission.update)
def category_update(category_id):
    """Update a category."""
    category = _get_category_or_404(category_id)

    form = TourneyCategoryUpdateForm(request.form)
    if not form.validate():
        return category_update_form(category_id, form)

    category_service.update_category(category.id, form.title.data.strip())

    flash_success(f'Die Kategorie "{category.title}" wurde aktualisiert.')
    return redirect_to('.category_index_for_party', party_id=category.party_id)


@blueprint.route('/categories/<uuid:category_id>/up', methods=['POST'])
@permission_required(TourneyCategoryPermission.update)
@respond_no_content
def category_move_up(category_id):
    """Move a category upwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        category_service.move_category_up(category.id)
    except ValueError:
        flash_error(
            f'Die Kategorie "{category.title}" befindet sich bereits ganz oben.'
        )
    else:
        flash_success(
            f'Die Kategorie "{category.title}" '
            'wurde eine Position nach oben verschoben.'
        )


@blueprint.route('/categories/<uuid:category_id>/down', methods=['POST'])
@permission_required(TourneyCategoryPermission.update)
@respond_no_content
def category_move_down(category_id):
    """Move a category downwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        category_service.move_category_down(category.id)
    except ValueError:
        flash_error(
            f'Die Kategorie "{category.title}" befindet sich bereits '
            'ganz unten.'
        )
    else:
        flash_success(
            f'Die Kategorie "{category.title}" '
            'wurde eine Position nach unten verschoben.'
        )


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_category_or_404(category_id):
    category = category_service.find_category(category_id)

    if category is None:
        abort(404)

    return category
