"""
byceps.blueprints.admin.board.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from flask import abort, request
from flask_babel import gettext

from ....services.board import board_service
from ....services.board import (
    category_command_service as board_category_command_service,
    category_query_service as board_category_query_service,
    posting_query_service as board_posting_query_service,
    topic_query_service as board_topic_query_service,
)
from ....services.board.transfer.models import Board, Category
from ....services.brand import service as brand_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, redirect_to, respond_no_content

from .forms import BoardCreateForm, CategoryCreateForm, CategoryUpdateForm


blueprint = create_blueprint('board_admin', __name__)


@dataclass(frozen=True)
class BoardStats:
    category_count: int
    topic_count: int
    posting_count: int


# -------------------------------------------------------------------- #
# boards


@blueprint.get('/brands/<brand_id>')
@permission_required('board_category.view')
@templated
def board_index_for_brand(brand_id):
    """List categories for that brand."""
    brand = _get_brand_or_404(brand_id)

    boards = board_service.get_boards_for_brand(brand.id)
    board_ids = [board.id for board in boards]

    stats_by_board_id = {
        board_id: BoardStats(
            board_category_query_service.count_categories_for_board(board_id),
            board_topic_query_service.count_topics_for_board(board_id),
            board_posting_query_service.count_postings_for_board(board_id),
        )
        for board_id in board_ids
    }

    return {
        'boards': boards,
        'brand': brand,
        'stats_by_board_id': stats_by_board_id,
    }


@blueprint.get('/boards/<board_id>')
@permission_required('board_category.view')
@templated
def board_view(board_id):
    """View the board."""
    board = _get_board_or_404(board_id)

    brand = brand_service.find_brand(board.brand_id)

    categories = board_category_query_service.get_categories(board.id)

    return {
        'board_id': board.id,
        'board_brand_id': board.brand_id,
        'brand': brand,
        'categories': categories,
    }


@blueprint.get('/for_brand/<brand_id>/boards/create')
@permission_required('board.create')
@templated
def board_create_form(brand_id, erroneous_form=None):
    """Show form to create a board."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else BoardCreateForm()

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.post('/for_brand/<brand_id>/boards')
@permission_required('board.create')
def board_create(brand_id):
    """Create a board."""
    brand = _get_brand_or_404(brand_id)

    form = BoardCreateForm(request.form)
    if not form.validate():
        return board_create_form(brand.id, form)

    board_id = form.board_id.data.strip().lower()

    board = board_service.create_board(brand.id, board_id)

    flash_success(
        gettext(
            'Board with ID "%(board_id)s" has been created.',
            board_id=board.id,
        )
    )
    return redirect_to('.board_view', board_id=board.id)


# -------------------------------------------------------------------- #
# categories


@blueprint.get('/categories/for_board/<board_id>/create')
@permission_required('board_category.create')
@templated
def category_create_form(board_id, erroneous_form=None):
    """Show form to create a category."""
    board = _get_board_or_404(board_id)

    brand = brand_service.find_brand(board.brand_id)

    form = erroneous_form if erroneous_form else CategoryCreateForm()

    return {
        'board': board,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/categories/for_board/<board_id>')
@permission_required('board_category.create')
def category_create(board_id):
    """Create a category."""
    board = _get_board_or_404(board_id)

    form = CategoryCreateForm(request.form)
    if not form.validate():
        return category_create_form(board.id, form)

    slug = form.slug.data.strip().lower()
    title = form.title.data.strip()
    description = form.description.data.strip()

    category = board_category_command_service.create_category(
        board.id, slug, title, description
    )

    flash_success(
        gettext(
            'Category "%(category_title)s" has been created.',
            category_title=category.title,
        )
    )
    return redirect_to('.board_view', board_id=board.id)


@blueprint.get('/categories/<uuid:category_id>/update')
@permission_required('board_category.update')
@templated
def category_update_form(category_id, erroneous_form=None):
    """Show form to update the category."""
    category = _get_category_or_404(category_id)

    board = board_service.find_board(category.board_id)
    brand = brand_service.find_brand(board.brand_id)

    form = (
        erroneous_form if erroneous_form else CategoryUpdateForm(obj=category)
    )

    return {
        'category': category,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/categories/<uuid:category_id>')
@permission_required('board_category.update')
def category_update(category_id):
    """Update the category."""
    category = _get_category_or_404(category_id)

    form = CategoryUpdateForm(request.form)
    if not form.validate():
        return category_update_form(category_id, form)

    slug = form.slug.data
    title = form.title.data
    description = form.description.data

    category = board_category_command_service.update_category(
        category.id, slug, title, description
    )

    flash_success(
        gettext(
            'Category "%(category_title)s" has been updated.',
            category_title=category.title,
        )
    )
    return redirect_to('.board_view', board_id=category.board_id)


@blueprint.post('/categories/<uuid:category_id>/flags/hidden')
@permission_required('board_category.update')
@respond_no_content
def category_hide(category_id):
    """Hide the category."""
    category = _get_category_or_404(category_id)

    board_category_command_service.hide_category(category.id)

    flash_success(
        gettext(
            'Category "%(category_title)s" has been hidden.',
            category_title=category.title,
        )
    )


@blueprint.delete('/categories/<uuid:category_id>/flags/hidden')
@permission_required('board_category.update')
@respond_no_content
def category_unhide(category_id):
    """Un-hide the category."""
    category = _get_category_or_404(category_id)

    board_category_command_service.unhide_category(category.id)

    flash_success(
        gettext(
            'Category "%(category_title)s" has been made visible.',
            category_title=category.title,
        )
    )


@blueprint.post('/categories/<uuid:category_id>/up')
@permission_required('board_category.update')
@respond_no_content
def category_move_up(category_id):
    """Move the category upwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        board_category_command_service.move_category_up(category.id)
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
                'Category "%(category_title)s" has been moved upwards by one position.',
                category_title=category.title,
            )
        )


@blueprint.post('/categories/<uuid:category_id>/down')
@permission_required('board_category.update')
@respond_no_content
def category_move_down(category_id):
    """Move the category downwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        board_category_command_service.move_category_down(category.id)
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
                'Category "%(category_title)s" has been moved downwards by one position.',
                category_title=category.title,
            )
        )


@blueprint.delete('/categories/<uuid:category_id>')
@permission_required('board_category.create')
@respond_no_content
def category_delete(category_id):
    """Delete a category."""
    category = _get_category_or_404(category_id)

    try:
        board_category_command_service.delete_category(category.id)
    except Exception:
        flash_error(
            gettext(
                'Category "%(category_title)s" could not be deleted.',
                category_title=category.title,
            )
        )
    else:
        flash_success(
            gettext(
                'Category "%(category_title)s" has been deleted.',
                category_title=category.title,
            )
        )


# -------------------------------------------------------------------- #
# helpers


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand


def _get_board_or_404(board_id) -> Board:
    board = board_service.find_board(board_id)

    if board is None:
        abort(404)

    return board


def _get_category_or_404(category_id) -> Category:
    category = board_category_query_service.find_category_by_id(category_id)

    if category is None:
        abort(404)

    return category
