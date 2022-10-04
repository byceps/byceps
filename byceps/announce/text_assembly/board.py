"""
byceps.announce.text_assembly.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from ...events.board import (
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
)
from ...services.board import board_topic_query_service
from ...services.board.transfer.models import TopicID
from ...services.brand import brand_service

from ._helpers import get_screen_name_or_fallback, with_locale


@with_locale
def assemble_text_for_board_topic_created(
    event: BoardTopicCreated,
    webhook_format: str,
) -> str:
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(topic_creator_screen_name)s has created topic "%(topic_title)s"%(board_label_segment)s: %(url)s',
        topic_creator_screen_name=topic_creator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        url=url,
    )


@with_locale
def assemble_text_for_board_topic_hidden(
    event: BoardTopicHidden,
    webhook_format: str,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(moderator_screen_name)s has hidden topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )


@with_locale
def assemble_text_for_board_topic_unhidden(
    event: BoardTopicUnhidden,
    webhook_format: str,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(moderator_screen_name)s has unhidden topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )


@with_locale
def assemble_text_for_board_topic_locked(
    event: BoardTopicLocked,
    webhook_format: str,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(moderator_screen_name)s has closed topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )


@with_locale
def assemble_text_for_board_topic_unlocked(
    event: BoardTopicUnlocked,
    webhook_format: str,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(moderator_screen_name)s has reopened topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )


@with_locale
def assemble_text_for_board_topic_pinned(
    event: BoardTopicPinned,
    webhook_format: str,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(moderator_screen_name)s has pinned topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )


@with_locale
def assemble_text_for_board_topic_unpinned(
    event: BoardTopicUnpinned,
    webhook_format: str,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(moderator_screen_name)s has unpinned topic "%(topic_title)s" by %(topic_creator_screen_name)s%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        url=url,
    )


@with_locale
def assemble_text_for_board_topic_moved(
    event: BoardTopicMoved,
    webhook_format: str,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(moderator_screen_name)s has moved topic "%(topic_title)s" by %(topic_creator_screen_name)s from "%(old_category_title)s" to "%(new_category_title)s"%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        topic_creator_screen_name=topic_creator_screen_name,
        old_category_title=event.old_category_title,
        new_category_title=event.new_category_title,
        url=url,
    )


@with_locale
def assemble_text_for_board_posting_created(
    event: BoardPostingCreated,
    webhook_format: str,
) -> str:
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(posting_creator_screen_name)s replied in topic "%(topic_title)s"%(board_label_segment)s: %(url)s',
        posting_creator_screen_name=posting_creator_screen_name,
        board_label_segment=board_label_segment,
        topic_title=event.topic_title,
        url=url,
    )


@with_locale
def assemble_text_for_board_posting_hidden(
    event: BoardPostingHidden,
    webhook_format: str,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(moderator_screen_name)s has hidden a reply by %(posting_creator_screen_name)s in topic "%(topic_title)s"%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        posting_creator_screen_name=posting_creator_screen_name,
        topic_title=event.topic_title,
        url=url,
    )


@with_locale
def assemble_text_for_board_posting_unhidden(
    event: BoardPostingUnhidden,
    webhook_format: str,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label_segment = _get_board_label_segment(
        event.topic_id, webhook_format
    )
    url = _format_url(event.url, webhook_format)

    return gettext(
        '%(moderator_screen_name)s has unhidden a reply by %(posting_creator_screen_name)s in topic "%(topic_title)s"%(board_label_segment)s: %(url)s',
        moderator_screen_name=moderator_screen_name,
        board_label_segment=board_label_segment,
        posting_creator_screen_name=posting_creator_screen_name,
        topic_title=event.topic_title,
        url=url,
    )


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
