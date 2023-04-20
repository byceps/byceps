"""
byceps.blueprints.site.board.views_category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, url_for
from flask_babel import gettext

from ....services.board import (
    board_category_query_service,
    board_last_view_service,
    board_topic_query_service,
)
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import respond_no_content_with_location

from ..site.navigation import subnavigation_for_view

from . import _helpers as h
from . import service
from .blueprint import blueprint


@blueprint.get('/')
@templated
@subnavigation_for_view('board')
def category_index():
    """List categories."""
    board_id = h.get_board_id()
    user = g.user

    h.require_board_access(board_id, user.id)

    categories = board_category_query_service.get_categories_with_last_updates(
        board_id
    )

    categories_with_flag = service.add_unseen_postings_flag_to_categories(
        categories, user
    )

    return {
        'categories': categories_with_flag,
    }


@blueprint.get('/categories/<slug>', defaults={'page': 1})
@blueprint.get('/categories/<slug>/pages/<int:page>')
@templated
@subnavigation_for_view('board')
def category_view(slug, page):
    """List latest topics in the category."""
    board_id = h.get_board_id()
    user = g.user

    h.require_board_access(board_id, user.id)

    category = board_category_query_service.find_category_by_slug(
        board_id, slug
    )

    if category is None:
        abort(404)

    if category.hidden:
        abort(404)

    if user.authenticated:
        board_last_view_service.mark_category_as_just_viewed(
            category.id, user.id
        )

    include_hidden = service.may_current_user_view_hidden()
    topics_per_page = service.get_topics_per_page_value()

    topics = board_topic_query_service.paginate_topics_of_category(
        category.id, include_hidden, page, topics_per_page
    )

    service.add_topic_creators(topics.items)
    service.add_topic_unseen_flag(topics.items, user)

    return {
        'category': category,
        'topics': topics,
    }


@blueprint.post('/categories/<category_id>/mark_all_topics_as_read')
@respond_no_content_with_location
def mark_all_topics_in_category_as_viewed(category_id):
    category = h.get_category_or_404(category_id)

    board_last_view_service.mark_all_topics_in_category_as_viewed(
        category_id, g.user.id
    )

    flash_success(
        gettext('All topics in this category have been marked as read.')
    )

    return url_for('.category_view', slug=category.slug)
