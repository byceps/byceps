"""
byceps.announce.irc.board
~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

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
from ...services.board.transfer.models import TopicID
from ...services.board import topic_query_service as board_topic_query_service
from ...services.brand import service as brand_service
from ...signals import board as board_signals
from ...util.jobqueue import enqueue

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC
from ._util import send_message


@board_signals.topic_created.connect
def _on_board_topic_created(
    sender, *, event: Optional[BoardTopicCreated] = None
) -> None:
    enqueue(announce_board_topic_created, event)


def announce_board_topic_created(event: BoardTopicCreated) -> None:
    """Announce that someone has created a board topic."""
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{topic_creator_screen_name} hat im {board_label} '
        f'das Thema "{event.topic_title}" erstellt: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)
    send_message(CHANNEL_PUBLIC, text)


@board_signals.topic_hidden.connect
def _on_board_topic_hidden(
    sender, *, event: Optional[BoardTopicHidden] = None
) -> None:
    enqueue(announce_board_topic_hidden, event)


def announce_board_topic_hidden(event: BoardTopicHidden) -> None:
    """Announce that a moderator has hidden a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'versteckt: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@board_signals.topic_unhidden.connect
def _on_board_topic_unhidden(
    sender, *, event: Optional[BoardTopicUnhidden] = None
) -> None:
    enqueue(announce_board_topic_unhidden, event)


def announce_board_topic_unhidden(event: BoardTopicUnhidden) -> None:
    """Announce that a moderator has made a board topic visible again."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'wieder sichtbar gemacht: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@board_signals.topic_locked.connect
def _on_board_topic_locked(
    sender, *, event: Optional[BoardTopicLocked] = None
) -> None:
    enqueue(announce_board_topic_locked, event)


def announce_board_topic_locked(event: BoardTopicLocked) -> None:
    """Announce that a moderator has locked a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'geschlossen: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@board_signals.topic_unlocked.connect
def _on_board_topic_unlocked(
    sender, *, event: Optional[BoardTopicUnlocked] = None
) -> None:
    enqueue(announce_board_topic_unlocked, event)


def announce_board_topic_unlocked(event: BoardTopicUnlocked) -> None:
    """Announce that a moderator has unlocked a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'wieder geöffnet: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@board_signals.topic_pinned.connect
def _on_board_topic_pinned(
    sender, *, event: Optional[BoardTopicPinned] = None
) -> None:
    enqueue(announce_board_topic_pinned, event)


def announce_board_topic_pinned(event: BoardTopicPinned) -> None:
    """Announce that a moderator has pinned a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'angepinnt: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@board_signals.topic_unpinned.connect
def _on_board_topic_unpinned(
    sender, *, event: Optional[BoardTopicUnpinned] = None
) -> None:
    enqueue(announce_board_topic_unpinned, event)


def announce_board_topic_unpinned(event: BoardTopicUnpinned) -> None:
    """Announce that a moderator has unpinned a board topic."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'wieder gelöst: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@board_signals.topic_moved.connect
def _on_board_topic_moved(
    sender, *, event: Optional[BoardTopicMoved] = None
) -> None:
    enqueue(announce_board_topic_moved, event)


def announce_board_topic_moved(event: BoardTopicMoved) -> None:
    """Announce that a moderator has moved a board topic to another category."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'aus "{event.old_category_title}" in "{event.new_category_title}" '
        f'verschoben: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@board_signals.posting_created.connect
def _on_board_posting_created(
    sender, *, event: Optional[BoardPostingCreated] = None
) -> None:
    enqueue(announce_board_posting_created, event)


def announce_board_posting_created(event: BoardPostingCreated) -> None:
    """Announce that someone has created a board posting."""
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    if event.topic_muted:
        return

    text = (
        f'{posting_creator_screen_name} hat im {board_label} '
        f'auf das Thema "{event.topic_title}" geantwortet: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)
    send_message(CHANNEL_PUBLIC, text)


@board_signals.posting_hidden.connect
def _on_board_posting_hidden(
    sender, *, event: Optional[BoardPostingHidden] = None
) -> None:
    enqueue(announce_board_posting_hidden, event)


def announce_board_posting_hidden(event: BoardPostingHidden) -> None:
    """Announce that a moderator has hidden a board posting."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{moderator_screen_name} hat im {board_label} '
        f'eine Antwort von {posting_creator_screen_name} '
        f'im Thema "{event.topic_title}" versteckt: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@board_signals.posting_unhidden.connect
def _on_board_posting_unhidden(
    sender, *, event: Optional[BoardPostingUnhidden] = None
) -> None:
    enqueue(announce_board_posting_unhidden, event)


def announce_board_posting_unhidden(event: BoardPostingUnhidden) -> None:
    """Announce that a moderator has made a board posting visible again."""
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    text = (
        f'{moderator_screen_name} hat im {board_label} '
        f'eine Antwort von {posting_creator_screen_name} '
        f'im Thema "{event.topic_title}" wieder sichtbar gemacht: {event.url}'
    )

    send_message(CHANNEL_ORGA_LOG, text)


def _get_board_label(topic_id: TopicID) -> str:
    topic = board_topic_query_service.find_topic_by_id(topic_id)
    brand_id = topic.category.board.brand_id
    brand = brand_service.find_brand(brand_id)
    return f'"{brand.title}"-Forum'
