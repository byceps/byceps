"""
byceps.announce.common.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

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

from ..helpers import get_screen_name_or_fallback


def assemble_text_for_board_topic_created(event: BoardTopicCreated) -> str:
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{topic_creator_screen_name} hat im {board_label} '
        f'das Thema "{event.topic_title}" erstellt: {event.url}'
    )


def assemble_text_for_board_topic_hidden(event: BoardTopicHidden) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'versteckt: {event.url}'
    )


def assemble_text_for_board_topic_unhidden(event: BoardTopicUnhidden) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'wieder sichtbar gemacht: {event.url}'
    )


def assemble_text_for_board_topic_locked(event: BoardTopicLocked) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'geschlossen: {event.url}'
    )


def assemble_text_for_board_topic_unlocked(event: BoardTopicUnlocked) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'wieder geöffnet: {event.url}'
    )


def assemble_text_for_board_topic_pinned(event: BoardTopicPinned) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'angepinnt: {event.url}'
    )


def assemble_text_for_board_topic_unpinned(event: BoardTopicUnpinned) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'wieder gelöst: {event.url}'
    )


def assemble_text_for_board_topic_moved(event: BoardTopicMoved) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{moderator_screen_name} hat im {board_label} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'aus "{event.old_category_title}" in "{event.new_category_title}" '
        f'verschoben: {event.url}'
    )


def assemble_text_for_board_posting_created(event: BoardPostingCreated) -> str:
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{posting_creator_screen_name} hat im {board_label} '
        f'auf das Thema "{event.topic_title}" geantwortet: {event.url}'
    )


def assemble_text_for_board_posting_hidden(event: BoardPostingHidden) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{moderator_screen_name} hat im {board_label} '
        f'eine Antwort von {posting_creator_screen_name} '
        f'im Thema "{event.topic_title}" versteckt: {event.url}'
    )


def assemble_text_for_board_posting_unhidden(
    event: BoardPostingUnhidden,
) -> str:
    moderator_screen_name = get_screen_name_or_fallback(
        event.moderator_screen_name
    )
    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )
    board_label = _get_board_label(event.topic_id)

    return (
        f'{moderator_screen_name} hat im {board_label} '
        f'eine Antwort von {posting_creator_screen_name} '
        f'im Thema "{event.topic_title}" wieder sichtbar gemacht: {event.url}'
    )


# helpers


def _get_board_label(topic_id: TopicID) -> str:
    topic = board_topic_query_service.find_topic_by_id(topic_id)
    brand_id = topic.category.board.brand_id
    brand = brand_service.find_brand(brand_id)
    return f'"{brand.title}"-Forum'
