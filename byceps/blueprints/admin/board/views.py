"""
byceps.blueprints.admin.board.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple

from flask import abort, request

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
from ....util.views import redirect_to, respond_no_content

from ...common.authorization.decorators import permission_required
from ...common.authorization.registry import permission_registry
from ...site.board.authorization import BoardPermission

from .authorization import BoardCategoryPermission
from .forms import BoardCreateForm, CategoryCreateForm, CategoryUpdateForm


blueprint = create_blueprint('board_admin', __name__)


permission_registry.register_enum(BoardPermission)
permission_registry.register_enum(BoardCategoryPermission)


BoardStats = namedtuple('BoardStats', [
    'category_count',
    'topic_count',
    'posting_count',
])


# -------------------------------------------------------------------- #
# boards


@blueprint.route('/brands/<brand_id>')
@permission_required(BoardCategoryPermission.view)
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


@blueprint.route('/boards/<board_id>')
@permission_required(BoardCategoryPermission.view)
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


@blueprint.route('/for_brand/<brand_id>/boards/create')
@permission_required(BoardPermission.create)
@templated
def board_create_form(brand_id, erroneous_form=None):
    """Show form to create a board."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else BoardCreateForm()

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.route('/for_brand/<brand_id>/boards', methods=['POST'])
@permission_required(BoardPermission.create)
def board_create(brand_id):
    """Create a board."""
    brand = _get_brand_or_404(brand_id)

    form = BoardCreateForm(request.form)
    if not form.validate():
        return board_create_form(brand.id, form)

    board_id = form.board_id.data.strip().lower()

    board = board_service.create_board(brand.id, board_id)

    flash_success(f'Das Forum mit der ID "{board.id}" wurde angelegt.')
    return redirect_to('.board_view', board_id=board.id)


# -------------------------------------------------------------------- #
# categories


@blueprint.route('/for_board/<board_id>/create')
@permission_required(BoardCategoryPermission.create)
@templated
def category_create_form(board_id, erroneous_form=None):
    """Show form to create a category."""
    board = _get_board_or_404(board_id)

    brand = brand_service.find_brand(board.brand_id)

    form = erroneous_form if erroneous_form else CategoryCreateForm()

    return {
        'board_id': board_id,
        'brand': brand,
        'form': form,
    }


@blueprint.route('/for_board/<board_id>', methods=['POST'])
@permission_required(BoardCategoryPermission.create)
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

    flash_success(f'Die Kategorie "{category.title}" wurde angelegt.')
    return redirect_to('.board_view', board_id=board.id)


@blueprint.route('/categories/<uuid:category_id>/update')
@permission_required(BoardCategoryPermission.update)
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


@blueprint.route('/categories/<uuid:category_id>', methods=['POST'])
@permission_required(BoardCategoryPermission.update)
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

    flash_success(f'Die Kategorie "{category.title}" wurde aktualisiert.')
    return redirect_to('.board_view', board_id=category.board_id)


@blueprint.route(
    '/categories/<uuid:category_id>/flags/hidden', methods=['POST']
)
@permission_required(BoardCategoryPermission.update)
@respond_no_content
def category_hide(category_id):
    """Hide the category."""
    category = _get_category_or_404(category_id)

    board_category_command_service.hide_category(category.id)

    flash_success(f'Die Kategorie "{category.title}" wurde versteckt.')


@blueprint.route(
    '/categories/<uuid:category_id>/flags/hidden', methods=['DELETE']
)
@permission_required(BoardCategoryPermission.update)
@respond_no_content
def category_unhide(category_id):
    """Un-hide the category."""
    category = _get_category_or_404(category_id)

    board_category_command_service.unhide_category(category.id)

    flash_success(f'Die Kategorie "{category.title}" wurde sichtbar gemacht.')


@blueprint.route('/categories/<uuid:category_id>/up', methods=['POST'])
@permission_required(BoardCategoryPermission.update)
@respond_no_content
def category_move_up(category_id):
    """Move the category upwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        board_category_command_service.move_category_up(category.id)
    except ValueError:
        flash_error(
            f'Die Kategorie "{category.title}" befindet sich bereits ganz oben.'
        )
    else:
        flash_success(
            f'Die Kategorie "{category.title}" wurde '
            'eine Position nach oben verschoben.'
        )


@blueprint.route('/categories/<uuid:category_id>/down', methods=['POST'])
@permission_required(BoardCategoryPermission.update)
@respond_no_content
def category_move_down(category_id):
    """Move the category downwards by one position."""
    category = _get_category_or_404(category_id)

    try:
        board_category_command_service.move_category_down(category.id)
    except ValueError:
        flash_error(
            f'Die Kategorie "{category.title}" befindet sich bereits '
            'ganz unten.'
        )
    else:
        flash_success(
            f'Die Kategorie "{category.title}" wurde '
            'eine Position nach unten verschoben.'
        )


@blueprint.route('/categories/<uuid:category_id>', methods=['DELETE'])
@permission_required(BoardCategoryPermission.create)
@respond_no_content
def category_delete(category_id):
    """Delete a category."""
    category = _get_category_or_404(category_id)

    try:
        board_category_command_service.delete_category(category.id)
    except Exception:
        flash_error(
            f'Die Kategorie "{category.title}" konnte nicht gelöscht werden.'
        )
    else:
        flash_success(f'Die Kategorie "{category.title}" wurde gelöscht.')


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
