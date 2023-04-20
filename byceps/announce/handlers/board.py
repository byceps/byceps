"""
byceps.announce.handlers.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps
from typing import Optional

from flask_babel import gettext

from byceps.announce.helpers import (
    Announcement,
    get_screen_name_or_fallback,
    matches_selectors,
    with_locale,
)
from byceps.events.board import (
    BoardPostingCreated,
    BoardPostingHidden,
    BoardPostingUnhidden,
    BoardTopicCreated,
    BoardTopicHidden,
    BoardTopicLocked,
    BoardTopicMoved,
    BoardTopicPinned,
    BoardTopicUnhidden,
    BoardTopicUnlocked,
    BoardTopicUnpinned,
    _BoardEvent,
)
from byceps.services.board import board_topic_query_service
from byceps.services.board.models import TopicID
from byceps.services.brand import brand_service
from byceps.services.webhooks.models import OutgoingWebhook


def apply_selectors(handler):
    @wraps(handler)
    def wrapper(
        event: _BoardEvent, webhook: OutgoingWebhook
    ) -> Optional[Announcement]:
        board_id = str(event.board_id)
        if not matches_selectors(event, webhook, 'board_id', board_id):
            return None

        return handler(event, webhook)

    return wrapper


@apply_selectors
@with_locale
def announce_board_topic_created(
    event: BoardTopicCreated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that someone has created a board topic."""
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(topic_creator_screen_name)s has created topic "%(topic_title)s"%(board_label_segment)s: %(url)s',
        topic_creator_screen_name=topic_creator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_topic_hidden(
    event: BoardTopicHidden, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has hidden a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(moderator_screen_name)s has hidden topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_topic_unhidden(
    event: BoardTopicUnhidden, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has made a board topic visible again."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(moderator_screen_name)s has unhidden topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_topic_locked(
    event: BoardTopicLocked, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has locked a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(moderator_screen_name)s has closed topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_topic_unlocked(
    event: BoardTopicUnlocked, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has unlocked a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(moderator_screen_name)s has reopened topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_topic_pinned(
    event: BoardTopicPinned, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has pinned a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(moderator_screen_name)s has pinned topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_topic_unpinned(
    event: BoardTopicUnpinned, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has unpinned a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(moderator_screen_name)s has unpinned topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_topic_moved(
    event: BoardTopicMoved, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has moved a board topic to another category."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(moderator_screen_name)s has moved topic "%(topic_title)s" by %(topic_creator_screen_name)s from "%(old_category_title)s" to "%(new_category_title)s"%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        old_category_title=event.old_category_title,
        new_category_title=event.new_category_title,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_posting_created(
    event: BoardPostingCreated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that someone has created a board posting."""
    if event.topic_muted:
        return None

    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(posting_creator_screen_name)s replied in topic "%(topic_title)s"%(board_label_segment)s: %(url)s',
        posting_creator_screen_name=posting_creator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_posting_hidden(
    event: BoardPostingHidden, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has hidden a board posting."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(moderator_screen_name)s has hidden a reply by %(posting_creator_screen_name)s in topic "%(topic_title)s"%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        posting_creator_screen_name=posting_creator_screen_name,
        topic_title=event.topic_title,
        url=url,
    )

    return Announcement(text)


@apply_selectors
@with_locale
def announce_board_posting_unhidden(
    event: BoardPostingUnhidden, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has made a board posting visible again."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook.format
    )
    url = _format_url(event.url, webhook.format)

    text = gettext(
        '%(moderator_screen_name)s has unhidden a reply by %(posting_creator_screen_name)s in topic "%(topic_title)s"%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        posting_creator_screen_name=posting_creator_screen_name,
        topic_title=event.topic_title,
        url=url,
    )

    return Announcement(text)


# helpers


def _get_board_label(topic_id: TopicID) -> str:
    topic = board_topic_query_service.get_topic(topic_id)
    brand_id = topic.category.board.brand_id
    brand = brand_service.get_brand(brand_id)
    return gettext('"%(brand_title)s" board', brand_title=brand.title)


def _get_board_label_segment(topic_id: TopicID, webhook_format: str) -> str:
    if webhook_format != 'weitersager':
        return ''

    board_label = _get_board_label(topic_id)
    return gettext(' in %(board_label)s', board_label=board_label)


def _format_url(url: str, webhook_format: str) -> str:
    return _escape_url_for_discord(url) if webhook_format == 'discord' else url


def _escape_url_for_discord(url: str) -> str:
    """Wrap URL in angle brackets (``<…>``) as that prevents preview
    embedding on Discord.
    """
    return f'<{url}>'
