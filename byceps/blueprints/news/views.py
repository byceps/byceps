"""
byceps.blueprints.news.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, current_app, g

from ...services.news import service as news_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated


blueprint = create_blueprint('news', __name__)


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/pages/<int:page>')
@templated
def index(page):
    """Show a page of news items."""
    items_per_page = _get_items_per_page_value()

    items = news_service.get_items_paginated(g.brand_id, page, items_per_page,
                                             published_only=True)

    return {
        'items': items,
        'page': page,
    }


@blueprint.route('/<slug>')
@templated
def view(slug):
    """Show a single news item."""
    item = news_service.find_item_by_slug(g.brand_id, slug)

    if item is None:
        abort(404)

    return {
        'item': item,
    }


def _get_items_per_page_value():
    return int(current_app.config['NEWS_ITEMS_PER_PAGE'])
