"""
byceps.blueprints.board.views_category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, url_for

from ...services.board import \
    category_query_service as board_category_query_service, \
    last_view_service as board_last_view_service, \
    topic_query_service as board_topic_query_service
from ...util.framework.templating import templated
from ...util.views import respond_no_content_with_location

from .blueprint import blueprint
from . import _helpers as h, service


@blueprint.route('/')
@templated
def category_index():
    """List categories."""
    board_id = h.get_board_id()
    user = g.current_user

    h.require_board_access(board_id, user.id)

    categories = board_category_query_service \
        .get_categories_with_last_updates(board_id)

    categories_with_flag = service.add_unseen_postings_flag_to_categories(
        categories, user)

    return {
        'categories': categories_with_flag,
    }


@blueprint.route('/categories/<slug>', defaults={'page': 1})
@blueprint.route('/categories/<slug>/pages/<int:page>')
@templated
def category_view(slug, page):
    """List latest topics in the category."""
    board_id = h.get_board_id()
    user = g.current_user

    h.require_board_access(board_id, user.id)

    category = board_category_query_service \
        .find_category_by_slug(board_id, slug)

    if category is None:
        abort(404)

    if category.hidden:
        abort(404)

    if not user.is_anonymous:
        board_last_view_service.mark_category_as_just_viewed(category.id,
                                                             user.id)

    topics_per_page = service.get_topics_per_page_value()

    topics = board_topic_query_service \
        .paginate_topics_of_category(category.id, user, page, topics_per_page)

    service.add_topic_creators(topics.items)
    service.add_topic_unseen_flag(topics.items, user)

    return {
        'category': category,
        'topics': topics,
    }


@blueprint.route('/categories/<category_id>/mark_all_topics_as_read', methods=['POST'])
@respond_no_content_with_location
def mark_all_topics_in_category_as_viewed(category_id):
    category = h.get_category_or_404(category_id)

    board_last_view_service.mark_all_topics_in_category_as_viewed(
        category_id, g.current_user.id)

    return url_for('.category_view', slug=category.slug)
