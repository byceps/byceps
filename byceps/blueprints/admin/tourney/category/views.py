"""
byceps.blueprints.admin.tourney.category.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from .....services.party import party_service
from .....services.tourney import tourney_category_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to, respond_no_content

from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('tourney_category_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('tourney_category.view')
@templated
def index(party_id):
    """List tourney categories for that party."""
    party = _get_party_or_404(party_id)

    categories = tourney_category_service.get_categories_for_party(party.id)

    return {
        'party': party,
        'categories': categories,
    }


@blueprint.get('/for_party/<party_id>/create')
@permission_required('tourney_category.administrate')
@templated
def create_form(party_id, erroneous_form=None):
    """Show form to create a category."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/for_party/<party_id>')
@permission_required('tourney_category.administrate')
def create(party_id):
    """Create a category."""
    party = _get_party_or_404(party_id)

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(party_id, form)

    title = form.title.data.strip()

    category = tourney_category_service.create_category(party.id, title)

    flash_success(
        gettext('Category "%(title)s" has been created.', title=category.title)
    )
    return redirect_to('.index', party_id=category.party_id)


@blueprint.get('/categories/<uuid:category_id>/update')
@permission_required('tourney_category.administrate')
@templated
def update_form(category_id, erroneous_form=None):
    """Show form to update a category."""
    category = _get_category_or_404(category_id)

    party = party_service.get_party(category.party_id)

    form = erroneous_form if erroneous_form else UpdateForm(obj=category)

    return {
        'category': category,
        'party': party,
        'form': form,
    }


@blueprint.post('/categories/<uuid:category_id>')
@permission_required('tourney_category.administrate')
def update(category_id):
    """Update a category."""
    category = _get_category_or_404(category_id)

    form = UpdateForm(request.form)
    if not form.validate():
        return update_form(category_id, form)

    tourney_category_service.update_category(
        category.id, form.title.data.strip()
    )

    flash_success(
        gettext('Category "%(title)s" has been updated.', title=category.title)
    )
    return redirect_to('.index', party_id=category.party_id)


@blueprint.post('/categories/<uuid:category_id>/up')
@permission_required('tourney_category.administrate')
@respond_no_content
def move_up(category_id):
    """Move a category upwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        tourney_category_service.move_category_up(category.id)
    except ValueError:
        flash_error(
            gettext(
                'Category "%(title)s" is already at the top.',
                title=category.title,
            )
        )
    else:
        flash_success(
            gettext(
                'Category "%(title)s" has been moved upwards by one position.',
                title=category.title,
            )
        )


@blueprint.post('/categories/<uuid:category_id>/down')
@permission_required('tourney_category.administrate')
@respond_no_content
def move_down(category_id):
    """Move a category downwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        tourney_category_service.move_category_down(category.id)
    except ValueError:
        flash_error(
            gettext(
                'Category "%(title)s" is already at the bottom.',
                title=category.title,
            )
        )
    else:
        flash_success(
            gettext(
                'Category "%(title)s" has been moved downwards by one position.',
                title=category.title,
            )
        )


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_category_or_404(category_id):
    category = tourney_category_service.find_category(category_id)

    if category is None:
        abort(404)

    return category
