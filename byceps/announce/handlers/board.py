"""
byceps.announce.handlers.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from functools import wraps

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    matches_selectors,
    with_locale,
)
from byceps.events.board import (
    _BoardEvent,
    BoardPostingCreatedEvent,
    BoardPostingHiddenEvent,
    BoardPostingUnhiddenEvent,
    BoardTopicCreatedEvent,
    BoardTopicHiddenEvent,
    BoardTopicLockedEvent,
    BoardTopicMovedEvent,
    BoardTopicPinnedEvent,
    BoardTopicUnhiddenEvent,
    BoardTopicUnlockedEvent,
    BoardTopicUnpinnedEvent,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


def apply_selectors(handler):
    @wraps(handler)
    def wrapper(
        event_name: str, event: _BoardEvent, webhook: OutgoingWebhook
    ) -> Announcement | None:
        board_id = str(event.board_id)
        if not matches_selectors(event_name, webhook, 'board_id', board_id):
            return None

        return handler(event_name, event, webhook)

    return wrapper


@apply_selectors
@with_locale
def announce_board_topic_created(
    event_name: str, event: BoardTopicCreatedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that someone has created a board topic."""
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardTopicHiddenEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a moderator has hidden a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardTopicUnhiddenEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a moderator has made a board topic visible again."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardTopicLockedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a moderator has locked a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardTopicUnlockedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a moderator has unlocked a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardTopicPinnedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a moderator has pinned a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardTopicUnpinnedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a moderator has unpinned a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardTopicMovedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a moderator has moved a board topic to another category."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardPostingCreatedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that someone has created a board posting."""
    if event.topic_muted:
        return None

    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardPostingHiddenEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a moderator has hidden a board posting."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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
    event_name: str, event: BoardPostingUnhiddenEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a moderator has made a board posting visible again."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.brand_title, webhook.format
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


def _get_board_label_segment(brand_title: str, webhook_format: str) -> str:
    if webhook_format != 'weitersager':
        return ''

    board_label = gettext('"%(brand_title)s" board', brand_title=brand_title)
    return gettext(' in %(board_label)s', board_label=board_label)


def _format_url(url: str, webhook_format: str) -> str:
    return _escape_url_for_discord(url) if webhook_format == 'discord' else url


def _escape_url_for_discord(url: str) -> str:
    """Wrap URL in angle brackets (``<…>``) as that prevents preview
    embedding on Discord.
    """
    return f'<{url}>'
