"""
byceps.blueprints.news.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import dataclasses

from flask import abort, g

from ...services.news import html_service as news_html_service
from ...services.news import service as news_service
from ...services.site import settings_service as site_settings_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated

from ..admin.news.authorization import NewsItemPermission
from ..authorization.registry import permission_registry


blueprint = create_blueprint('news', __name__)


permission_registry.register_enum(NewsItemPermission)


DEFAULT_ITEMS_PER_PAGE = 4


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/pages/<int:page>')
@templated
def index(page):
    """Show a page of news items."""
    channel_id = _get_channel_id()
    items_per_page = _get_items_per_page_value()
    published_only = not _may_view_drafts(g.current_user)

    items = news_service.get_aggregated_items_paginated(
        channel_id, page, items_per_page, published_only=published_only
    )

    replacement_items = [
        _replace_body_with_rendered_body(item) for item in items.items
    ]
    items.items = replacement_items

    return {
        'items': items,
        'page': page,
    }


@blueprint.route('/<slug>')
@templated
def view(slug):
    """Show a single news item."""
    channel_id = _get_channel_id()
    published_only = not _may_view_drafts(g.current_user)

    item = news_service.find_aggregated_item_by_slug(
        channel_id, slug, published_only=published_only
    )

    if item is None:
        abort(404)

    item = _replace_body_with_rendered_body(item)

    return {
        'item': item,
    }


def _get_channel_id():
    channel_id = site_settings_service.find_setting_value(
        g.site_id, 'news_channel_id'
    )

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


def _replace_body_with_rendered_body(item):
    try:
        rendered_body = news_html_service.render_body(
            item.body, item.channel.id, item.images
        )
    except Exception as e:
        rendered_body = None  # Not the best error indicator.

    return dataclasses.replace(item, body=rendered_body)
