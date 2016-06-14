# -*- coding: utf-8 -*-

"""
byceps.blueprints.tourney_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import request, url_for

from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party.models import Party
from ..tourney.models.tourney_category import TourneyCategory

from .authorization import TourneyCategoryPermission
from .forms import TourneyCategoryCreateForm, TourneyCategoryUpdateForm
from . import service


blueprint = create_blueprint('tourney_admin', __name__)


permission_registry.register_enum(TourneyCategoryPermission)


@blueprint.route('/parties/<party_id>/categories')
@permission_required(TourneyCategoryPermission.list)
@templated
def category_index_for_party(party_id):
    """List tourney categories for that party."""
    party = get_party_or_404(party_id)

    categories = service.get_categories_for_party(party)

    return {
        'party': party,
        'categories': categories,
    }


@blueprint.route('/parties/<party_id>/categories/create')
@permission_required(TourneyCategoryPermission.create)
@templated
def category_create_form(party_id, erroneous_form=None):
    """Show form to create a category."""
    party = get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else TourneyCategoryCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/parties/<party_id>/categories', methods=['POST'])
@permission_required(TourneyCategoryPermission.create)
def category_create(party_id):
    """Create a category."""
    party = get_party_or_404(party_id)

    form = TourneyCategoryCreateForm(request.form)
    if not form.validate():
        return category_create_form(party_id, form)

    title = form.title.data.strip()

    category = service.create_category(party, title)

    flash_success('Die Kategorie "{}" wurde angelegt.', category.title)
    return redirect_to('.category_index_for_party', party_id=category.party.id)


@blueprint.route('/categories/<uuid:id>/update')
@permission_required(TourneyCategoryPermission.update)
@templated
def category_update_form(id, erroneous_form=None):
    """Show form to update a category."""
    category = TourneyCategory.query.get_or_404(id)

    form = erroneous_form if erroneous_form \
           else TourneyCategoryUpdateForm(obj=category)

    return {
        'category': category,
        'form': form,
    }


@blueprint.route('/categories/<uuid:id>', methods=['POST'])
@permission_required(TourneyCategoryPermission.update)
def category_update(id):
    """Update a category."""
    category = TourneyCategory.query.get_or_404(id)

    form = TourneyCategoryUpdateForm(request.form)
    if not form.validate():
        return category_update_form(id, form)

    service.update_category(category, form.title.data.strip())

    flash_success('Die Kategorie "{}" wurde aktualisiert.', category.title)
    return redirect_to('.category_index_for_party', party_id=category.party.id)


@blueprint.route('/categories/<uuid:id>/up', methods=['POST'])
@permission_required(TourneyCategoryPermission.update)
@respond_no_content_with_location
def category_move_up(id):
    """Move a category upwards by one position."""
    category = TourneyCategory.query.get_or_404(id)

    try:
        service.move_category_up(category)
    except ValueError:
        flash_error('Die Kategorie "{}" befindet sich bereits ganz oben.', category.title)
    else:
        flash_success('Die Kategorie "{}" wurde nach oben verschoben.', category.title)

    return url_for('.category_index_for_party', party_id=category.party.id)


def get_party_or_404(party_id):
    return Party.query.get_or_404(party_id)
