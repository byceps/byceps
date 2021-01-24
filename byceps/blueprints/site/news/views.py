"""
byceps.blueprints.site.news.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from ....services.news import service as news_item_service
from ....services.site import (
    service as site_service,
    settings_service as site_settings_service,
)
from ....util.authorization import register_permission_enum
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...admin.news.authorization import NewsItemPermission


blueprint = create_blueprint('news', __name__)


register_permission_enum(NewsItemPermission)


DEFAULT_ITEMS_PER_PAGE = 4


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/pages/<int:page>')
@templated
def index(page):
    """Show a page of news items."""
    channel_id = _get_channel_id()
    items_per_page = _get_items_per_page_value()
    published_only = not _may_view_drafts(g.user)

    items = news_item_service.get_aggregated_items_paginated(
        channel_id, page, items_per_page, published_only=published_only
    )

    return {
        'items': items,
        'page': page,
    }


@blueprint.route('/<slug>')
@templated
def view(slug):
    """Show a single news item."""
    channel_id = _get_channel_id()
    published_only = not _may_view_drafts(g.user)

    item = news_item_service.find_aggregated_item_by_slug(
        channel_id, slug, published_only=published_only
    )

    if item is None:
        abort(404)

    return {
        'item': item,
    }


def _get_channel_id():
    site = site_service.get_site(g.site_id)

    channel_id = site.news_channel_id
    if channel_id is None:
        abort(404)

    return channel_id


def _get_items_per_page_value():
    items_per_page = site_settings_service.find_setting_value(
        g.site_id, 'news_items_per_page'
    )

    if items_per_page is None:
        return DEFAULT_ITEMS_PER_PAGE

    return int(items_per_page)


def _may_view_drafts(user):
    return user.has_permission(NewsItemPermission.view_draft)
