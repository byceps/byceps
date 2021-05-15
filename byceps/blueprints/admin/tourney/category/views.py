"""
byceps.blueprints.admin.tourney.category.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from .....services.party import service as party_service
from .....services.tourney import category_service
from .....util.authorization import register_permission_enum
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to, respond_no_content

from ..authorization import TourneyCategoryPermission

from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('tourney_category_admin', __name__)


register_permission_enum(TourneyCategoryPermission)


@blueprint.get('/for_party/<party_id>')
@permission_required(TourneyCategoryPermission.view)
@templated
def index(party_id):
    """List tourney categories for that party."""
    party = _get_party_or_404(party_id)

    categories = category_service.get_categories_for_party(party.id)

    return {
        'party': party,
        'categories': categories,
    }


@blueprint.get('/for_party/<party_id>/create')
@permission_required(TourneyCategoryPermission.administrate)
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
@permission_required(TourneyCategoryPermission.administrate)
def create(party_id):
    """Create a category."""
    party = _get_party_or_404(party_id)

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(party_id, form)

    title = form.title.data.strip()

    category = category_service.create_category(party.id, title)

    flash_success(
        gettext(
            'Category "%(category_title)s" has been created.',
            category_title=category.title,
        )
    )
    return redirect_to('.index', party_id=category.party_id)


@blueprint.get('/categories/<uuid:category_id>/update')
@permission_required(TourneyCategoryPermission.administrate)
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
@permission_required(TourneyCategoryPermission.administrate)
def update(category_id):
    """Update a category."""
    category = _get_category_or_404(category_id)

    form = UpdateForm(request.form)
    if not form.validate():
        return update_form(category_id, form)

    category_service.update_category(category.id, form.title.data.strip())

    flash_success(
        gettext(
            'Category "%(category_title)s" has been updated.',
            category_title=category.title,
        )
    )
    return redirect_to('.index', party_id=category.party_id)


@blueprint.post('/categories/<uuid:category_id>/up')
@permission_required(TourneyCategoryPermission.administrate)
@respond_no_content
def move_up(category_id):
    """Move a category upwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        category_service.move_category_up(category.id)
    except ValueError:
        flash_error(
            gettext(
                'Category "%(category_title)s" is already at the top.',
                category_title=category.title,
            )
        )
    else:
        flash_success(
            gettext(
                'Category "%(category_title)s" has been moved upwards by one position.'
            )
        )


@blueprint.post('/categories/<uuid:category_id>/down')
@permission_required(TourneyCategoryPermission.administrate)
@respond_no_content
def move_down(category_id):
    """Move a category downwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        category_service.move_category_down(category.id)
    except ValueError:
        flash_error(
            gettext(
                'Category "%(category_title)s" is already at the bottom.',
                category_title=category.title,
            )
        )
    else:
        flash_success(
            gettext(
                'Category "%(category_title)s" has been moved downwards by one position.'
            )
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
