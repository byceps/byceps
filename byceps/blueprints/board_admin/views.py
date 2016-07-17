# -*- coding: utf-8 -*-

"""
byceps.blueprints.board_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import request, url_for

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..board.models.category import Category
from ..board import service as board_service

from .authorization import BoardCategoryPermission
from .forms import CategoryCreateForm, CategoryUpdateForm
from . import service


blueprint = create_blueprint('board_admin', __name__)


permission_registry.register_enum(BoardCategoryPermission)


@blueprint.route('/brands/<brand_id>')
@permission_required(BoardCategoryPermission.list)
@templated
def index_for_brand(brand_id):
    """List categories for that brand."""
    brand = get_brand_or_404(brand_id)

    categories = Category.query \
        .filter_by(brand=brand) \
        .order_by(Category.position) \
        .all()

    return {
        'brand': brand,
        'categories': categories,
    }


@blueprint.route('/for_brand/<brand_id>/create')
@permission_required(BoardCategoryPermission.create)
@templated
def category_create_form(brand_id, erroneous_form=None):
    """Show form to create a category."""
    brand = get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else CategoryCreateForm()

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.route('/for_brand/<brand_id>', methods=['POST'])
@permission_required(BoardCategoryPermission.create)
def category_create(brand_id):
    """Create a category."""
    brand = get_brand_or_404(brand_id)

    form = CategoryCreateForm(request.form)
    if not form.validate():
        return category_create_form(brand_id, form)

    position = form.position.data
    slug = form.slug.data.strip().lower()
    title = form.title.data.strip()
    description = form.description.data.strip()

    category = board_service.create_category(brand, position, slug, title,
                                             description)

    flash_success('Die Kategorie "{}" wurde angelegt.', category.title)
    return redirect_to('.index_for_brand', brand_id=brand.id)


@blueprint.route('/categories/<uuid:id>/update')
@permission_required(BoardCategoryPermission.update)
@templated
def category_update_form(id, erroneous_form=None):
    """Show form to update a category."""
    category = get_category_or_404(id)

    form = erroneous_form if erroneous_form \
           else CategoryUpdateForm(obj=category)

    return {
        'category': category,
        'form': form,
    }


@blueprint.route('/categories/<uuid:id>', methods=['POST'])
@permission_required(BoardCategoryPermission.update)
def category_update(id):
    """Update a category."""
    category = get_category_or_404(id)

    form = CategoryUpdateForm(request.form)
    if not form.validate():
        return category_update_form(id, form)

    category.position = form.position.data
    category.slug = form.slug.data.strip().lower()
    category.title = form.title.data.strip()
    category.description = form.description.data.strip()
    db.session.commit()

    flash_success('Die Kategorie "{}" wurde aktualisiert.', category.title)
    return redirect_to('.index_for_brand', brand_id=category.brand.id)


@blueprint.route('/categories/<uuid:id>/up', methods=['POST'])
@permission_required(BoardCategoryPermission.update)
@respond_no_content_with_location
def category_move_up(id):
    """Move a category upwards by one position."""
    category = get_category_or_404(id)

    try:
        service.move_category_up(category)
    except ValueError:
        flash_error('Die Kategorie "{}" befindet sich bereits ganz oben.', category.title)
    else:
        flash_success('Die Kategorie "{}" wurde eine Position nach oben verschoben.', category.title)

    return url_for('.index_for_brand', brand_id=category.brand.id)


@blueprint.route('/categories/<uuid:id>/down', methods=['POST'])
@permission_required(BoardCategoryPermission.update)
@respond_no_content_with_location
def category_move_down(id):
    """Move a category downwards by one position."""
    category = get_category_or_404(id)

    try:
        service.move_category_down(category)
    except ValueError:
        flash_error('Die Kategorie "{}" befindet sich bereits ganz unten.', category.title)
    else:
        flash_success('Die Kategorie "{}" wurde eine Position nach unten verschoben.', category.title)

    return url_for('.index_for_brand', brand_id=category.brand.id)


def get_brand_or_404(id):
    return Brand.query.get_or_404(id)


def get_category_or_404(id):
    return Category.query.get_or_404(id)
