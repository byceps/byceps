"""
byceps.services.board.blueprints.site.views_category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, url_for
from flask_babel import gettext

from byceps.services.board import (
    board_category_command_service,
    board_category_query_service,
    board_topic_command_service,
    board_topic_query_service,
)
from byceps.services.site.blueprints.site.navigation import (
    subnavigation_for_view,
)
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import respond_no_content_with_location

from . import _helpers as h, service
from .blueprint import blueprint


@blueprint.get('/')
@templated
@subnavigation_for_view('board')
def category_index():
    """List categories."""
    board_id = h.get_board_id()
    current_user = g.user

    h.require_board_access(board_id, current_user.id)

    categories = board_category_query_service.get_category_summaries(
        board_id, current_user
    )

    recent_topics = service.get_recent_topics()

    return {
        'categories': categories,
        'recent_topics': recent_topics,
    }


@blueprint.get('/categories/<slug>', defaults={'page': 1})
@blueprint.get('/categories/<slug>/pages/<int:page>')
@templated
@subnavigation_for_view('board')
def category_view(slug, page):
    """List latest topics in the category."""
    board_id = h.get_board_id()
    current_user = g.user

    h.require_board_access(board_id, current_user.id)

    category = board_category_query_service.find_category_by_slug(
        board_id, slug
    )

    if category is None:
        abort(404)

    if category.hidden:
        abort(404)

    if current_user.authenticated:
        board_category_command_service.mark_category_as_just_viewed(
            category.id, current_user.id
        )

    include_hidden = service.may_current_user_view_hidden()
    topics_per_page = service.get_topics_per_page_value()

    topics = board_topic_query_service.paginate_topics_of_category(
        category.id,
        page,
        topics_per_page,
        current_user,
        include_hidden=include_hidden,
    )

    return {
        'category': category,
        'topics': topics,
    }


@blueprint.post('/topics/mark_all_topics_as_read')
@respond_no_content_with_location
def mark_all_topics_as_viewed():
    board_topic_command_service.mark_all_topics_as_viewed(g.user.id)

    flash_success(gettext('All topics have been marked as read.'))

    return url_for('.category_index')


@blueprint.post('/categories/<category_id>/mark_all_topics_as_read')
@respond_no_content_with_location
def mark_all_topics_in_category_as_viewed(category_id):
    category = h.get_category_or_404(category_id)

    board_topic_command_service.mark_all_topics_in_category_as_viewed(
        category_id, g.user.id
    )

    flash_success(
        gettext('All topics in this category have been marked as read.')
    )

    return url_for('.category_view', slug=category.slug)
