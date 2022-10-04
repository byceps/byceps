"""
byceps.blueprints.site.news.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional, Union

from flask import abort, g

from ....services.news import service as news_item_service
from ....services.news.transfer.models import ChannelID, Item
from ....services.site import site_service, site_setting_service
from ....services.site.transfer.models import SiteID
from ....util.authorization import has_current_user_permission
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated


blueprint = create_blueprint('news', __name__)


DEFAULT_ITEMS_PER_PAGE = 4


@blueprint.get('/', defaults={'page': 1})
@blueprint.get('/pages/<int:page>')
@templated
def index(page):
    """Show a page of news items."""
    channel_ids = _get_channel_ids()
    items_per_page = _get_items_per_page_value()
    published_only = not _may_current_user_view_drafts()

    items = news_item_service.get_aggregated_items_paginated(
        channel_ids, page, items_per_page, published_only=published_only
    )

    return {
        'items': items,
        'page': page,
        'per_page': items_per_page,
    }


@blueprint.get('/<slug>')
@templated
def view(slug):
    """Show a single news item."""
    channel_ids = _get_channel_ids()
    published_only = not _may_current_user_view_drafts()

    item = news_item_service.find_aggregated_item_by_slug(
        channel_ids, slug, published_only=published_only
    )

    if item is None:
        abort(404)

    external_item_url = _get_external_url(item)

    return {
        'item': item,
        'external_item_url': external_item_url,
    }


def _get_channel_ids() -> Union[frozenset[ChannelID], set[ChannelID]]:
    site = site_service.get_site(g.site_id)

    if not site.news_channel_ids:
        abort(404)

    return site.news_channel_ids


def _get_items_per_page_value() -> int:
    items_per_page = site_setting_service.find_setting_value(
        g.site_id, 'news_items_per_page'
    )

    if items_per_page is None:
        return DEFAULT_ITEMS_PER_PAGE

    return int(items_per_page)


def _may_current_user_view_drafts() -> bool:
    return has_current_user_permission('news_item.view_draft')


def _get_external_url(item: Item) -> Optional[str]:
    announcement_site_id = item.channel.announcement_site_id
    if announcement_site_id is None:
        return None

    announcement_site = site_service.get_site(SiteID(announcement_site_id))
    return f'https://{announcement_site.server_name}/news/{item.slug}'
