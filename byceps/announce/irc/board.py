"""
byceps.announce.irc.board
~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...blueprints.board import signals
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
from ...services.board.models.topic import Topic as DbTopic
from ...services.board import (
    category_query_service as board_category_query_service,
    posting_query_service as board_posting_query_service,
    topic_query_service as board_topic_query_service,
)
from ...services.brand import service as brand_service
from ...services.user import service as user_service
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


@signals.topic_created.connect
def _on_board_topic_created(sender, *, event: BoardTopicCreated = None) -> None:
    enqueue(announce_board_topic_created, event)


def announce_board_topic_created(event: BoardTopicCreated) -> None:
    """Announce that someone has created a board topic."""
    channels = [CHANNEL_ORGA_LOG, CHANNEL_PUBLIC]

    topic = board_topic_query_service.find_topic_by_id(event.topic_id)
    topic_creator = user_service.find_user(topic.creator_id)
    board_label = _get_board_label(topic)

    text = (
        f'{topic_creator.screen_name} hat im {board_label} '
        f'das Thema "{topic.title}" erstellt: {event.url}'
    )

    send_message(channels, text)


@signals.topic_hidden.connect
def _on_board_topic_hidden(sender, *, event: BoardTopicHidden = None) -> None:
    enqueue(announce_board_topic_hidden, event)


def announce_board_topic_hidden(event: BoardTopicHidden) -> None:
    """Announce that a moderator has hidden a board topic."""
    channels = [CHANNEL_ORGA_LOG]

    topic = board_topic_query_service.find_topic_by_id(event.topic_id)
    topic_creator = user_service.find_user(topic.creator_id)
    board_label = _get_board_label(topic)
    moderator = user_service.find_user(event.moderator_id)

    text = (
        f'{moderator.screen_name} hat im {board_label} '
        f'das Thema "{topic.title}" von {topic_creator.screen_name} '
        f'versteckt: {event.url}'
    )

    send_message(channels, text)


@signals.topic_unhidden.connect
def _on_board_topic_unhidden(
    sender, *, event: BoardTopicUnhidden = None
) -> None:
    enqueue(announce_board_topic_unhidden, event)


def announce_board_topic_unhidden(event: BoardTopicUnhidden) -> None:
    """Announce that a moderator has made a board topic visible again."""
    channels = [CHANNEL_ORGA_LOG]

    topic = board_topic_query_service.find_topic_by_id(event.topic_id)
    topic_creator = user_service.find_user(topic.creator_id)
    board_label = _get_board_label(topic)
    moderator = user_service.find_user(event.moderator_id)

    text = (
        f'{moderator.screen_name} hat im {board_label} '
        f'das Thema "{topic.title}" von {topic_creator.screen_name} '
        f'wieder sichtbar gemacht: {event.url}'
    )

    send_message(channels, text)


@signals.topic_locked.connect
def _on_board_topic_locked(sender, *, event: BoardTopicLocked = None) -> None:
    enqueue(announce_board_topic_locked, event)


def announce_board_topic_locked(event: BoardTopicLocked) -> None:
    """Announce that a moderator has locked a board topic."""
    channels = [CHANNEL_ORGA_LOG]

    topic = board_topic_query_service.find_topic_by_id(event.topic_id)
    topic_creator = user_service.find_user(topic.creator_id)
    board_label = _get_board_label(topic)
    moderator = user_service.find_user(event.moderator_id)

    text = (
        f'{moderator.screen_name} hat im {board_label} '
        f'das Thema "{topic.title}" von {topic_creator.screen_name} '
        f'geschlossen: {event.url}'
    )

    send_message(channels, text)


@signals.topic_unlocked.connect
def _on_board_topic_unlocked(
    sender, *, event: BoardTopicUnlocked = None
) -> None:
    enqueue(announce_board_topic_unlocked, event)


def announce_board_topic_unlocked(event: BoardTopicUnlocked) -> None:
    """Announce that a moderator has unlocked a board topic."""
    channels = [CHANNEL_ORGA_LOG]

    topic = board_topic_query_service.find_topic_by_id(event.topic_id)
    topic_creator = user_service.find_user(topic.creator_id)
    board_label = _get_board_label(topic)
    moderator = user_service.find_user(event.moderator_id)

    text = (
        f'{moderator.screen_name} hat im {board_label} '
        f'das Thema "{topic.title}" von {topic_creator.screen_name} '
        f'wieder geöffnet: {event.url}'
    )

    send_message(channels, text)


@signals.topic_pinned.connect
def _on_board_topic_pinned(sender, *, event: BoardTopicPinned = None) -> None:
    enqueue(announce_board_topic_pinned, event)


def announce_board_topic_pinned(event: BoardTopicPinned) -> None:
    """Announce that a moderator has pinned a board topic."""
    channels = [CHANNEL_ORGA_LOG]

    topic = board_topic_query_service.find_topic_by_id(event.topic_id)
    topic_creator = user_service.find_user(topic.creator_id)
    board_label = _get_board_label(topic)
    moderator = user_service.find_user(event.moderator_id)

    text = (
        f'{moderator.screen_name} hat im {board_label} '
        f'das Thema "{topic.title}" von {topic_creator.screen_name} '
        f'angepinnt: {event.url}'
    )

    send_message(channels, text)


@signals.topic_unpinned.connect
def _on_board_topic_unpinned(
    sender, *, event: BoardTopicUnpinned = None
) -> None:
    enqueue(announce_board_topic_unpinned, event)


def announce_board_topic_unpinned(event: BoardTopicUnpinned) -> None:
    """Announce that a moderator has unpinned a board topic."""
    channels = [CHANNEL_ORGA_LOG]

    topic = board_topic_query_service.find_topic_by_id(event.topic_id)
    topic_creator = user_service.find_user(topic.creator_id)
    board_label = _get_board_label(topic)
    moderator = user_service.find_user(event.moderator_id)

    text = (
        f'{moderator.screen_name} hat im {board_label} '
        f'das Thema "{topic.title}" von {topic_creator.screen_name} '
        f'wieder gelöst: {event.url}'
    )

    send_message(channels, text)


@signals.topic_moved.connect
def _on_board_topic_moved(sender, *, event: BoardTopicMoved = None) -> None:
    enqueue(announce_board_topic_moved, event)


def announce_board_topic_moved(event: BoardTopicMoved) -> None:
    """Announce that a moderator has moved a board topic to another category."""
    channels = [CHANNEL_ORGA_LOG]

    topic = board_topic_query_service.find_topic_by_id(event.topic_id)
    topic_creator = user_service.find_user(topic.creator_id)
    board_label = _get_board_label(topic)
    old_category = board_category_query_service.find_category_by_id(
        event.old_category_id
    )
    new_category = board_category_query_service.find_category_by_id(
        event.new_category_id
    )
    moderator = user_service.find_user(event.moderator_id)

    text = (
        f'{moderator.screen_name} hat im {board_label} '
        f'das Thema "{topic.title}" von {topic_creator.screen_name} '
        f'aus "{old_category.title}" in "{new_category.title}" '
        f'verschoben: {event.url}'
    )

    send_message(channels, text)


@signals.posting_created.connect
def _on_board_posting_created(
    sender, *, event: BoardPostingCreated = None
) -> None:
    enqueue(announce_board_posting_created, event)


def announce_board_posting_created(event: BoardPostingCreated) -> None:
    """Announce that someone has created a board posting."""
    channels = [CHANNEL_ORGA_LOG, CHANNEL_PUBLIC]

    posting = board_posting_query_service.find_posting_by_id(event.posting_id)
    posting_creator = user_service.find_user(posting.creator_id)
    board_label = _get_board_label(posting.topic)

    # Ignore selected topics.
    if str(posting.topic_id) in {
        '6ca347b2-555e-4f46-b107-9b6a1c7b421c',
        'f57d9627-c0fc-4219-834f-981f0508e213',
    }:
        return

    text = (
        f'{posting_creator.screen_name} hat im {board_label} '
        f'auf das Thema "{posting.topic.title}" geantwortet: {event.url}'
    )

    send_message(channels, text)


@signals.posting_hidden.connect
def _on_board_posting_hidden(
    sender, *, event: BoardPostingHidden = None
) -> None:
    enqueue(announce_board_posting_hidden, event)


def announce_board_posting_hidden(event: BoardPostingHidden) -> None:
    """Announce that a moderator has hidden a board posting."""
    channels = [CHANNEL_ORGA_LOG]

    posting = board_posting_query_service.find_posting_by_id(event.posting_id)
    posting_creator = user_service.find_user(posting.creator_id)
    board_label = _get_board_label(posting.topic)
    moderator = user_service.find_user(event.moderator_id)

    text = (
        f'{moderator.screen_name} hat im {board_label} '
        f'eine Antwort von {posting_creator.screen_name} '
        f'im Thema "{posting.topic.title}" versteckt: {event.url}'
    )

    send_message(channels, text)


@signals.posting_unhidden.connect
def _on_board_posting_unhidden(
    sender, *, event: BoardPostingUnhidden = None
) -> None:
    enqueue(announce_board_posting_unhidden, event)


def announce_board_posting_unhidden(event: BoardPostingUnhidden) -> None:
    """Announce that a moderator has made a board posting visible again."""
    channels = [CHANNEL_ORGA_LOG]

    posting = board_posting_query_service.find_posting_by_id(event.posting_id)
    posting_creator = user_service.find_user(posting.creator_id)
    board_label = _get_board_label(posting.topic)
    moderator = user_service.find_user(event.moderator_id)

    text = (
        f'{moderator.screen_name} hat im {board_label} '
        f'eine Antwort von {posting_creator.screen_name} '
        f'im Thema "{posting.topic.title}" wieder sichtbar gemacht: {event.url}'
    )

    send_message(channels, text)


def _get_board_label(topic: DbTopic) -> str:
    brand_id = topic.category.board.brand_id
    brand = brand_service.find_brand(brand_id)
    return f'"{brand.title}"-Forum'
