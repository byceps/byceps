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

    return (
        f'{topic_creator_screen_name} hat{board_label_segment} '
        f'das Thema "{event.topic_title}" erstellt: {event.url}'
    )


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

    return (
        f'{moderator_screen_name} hat{board_label_segment} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'versteckt: {event.url}'
    )


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

    return (
        f'{moderator_screen_name} hat{board_label_segment} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'wieder sichtbar gemacht: {event.url}'
    )


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

    return (
        f'{moderator_screen_name} hat{board_label_segment} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'geschlossen: {event.url}'
    )


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

    return (
        f'{moderator_screen_name} hat{board_label_segment} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'wieder geöffnet: {event.url}'
    )


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

    return (
        f'{moderator_screen_name} hat{board_label_segment} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'angepinnt: {event.url}'
    )


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

    return (
        f'{moderator_screen_name} hat{board_label_segment} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'wieder gelöst: {event.url}'
    )


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

    return (
        f'{moderator_screen_name} hat{board_label_segment} das Thema '
        f'"{event.topic_title}" von {topic_creator_screen_name} '
        f'aus "{event.old_category_title}" in "{event.new_category_title}" '
        f'verschoben: {event.url}'
    )


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

    return (
        f'{posting_creator_screen_name} hat{board_label_segment} '
        f'auf das Thema "{event.topic_title}" geantwortet: {event.url}'
    )


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

    return (
        f'{moderator_screen_name} hat{board_label_segment} '
        f'eine Antwort von {posting_creator_screen_name} '
        f'im Thema "{event.topic_title}" versteckt: {event.url}'
    )


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

    return (
        f'{moderator_screen_name} hat{board_label_segment} '
        f'eine Antwort von {posting_creator_screen_name} '
        f'im Thema "{event.topic_title}" wieder sichtbar gemacht: {event.url}'
    )


# helpers


def _get_board_label(topic_id: TopicID) -> str:
    topic = board_topic_query_service.find_topic_by_id(topic_id)
    brand_id = topic.category.board.brand_id
    brand = brand_service.find_brand(brand_id)
    return f'"{brand.title}"-Forum'


def _get_board_label_segment(topic_id: TopicID, webhook_format: str) -> str:
    if webhook_format != 'weitersager':
        return ''

    board_label = _get_board_label(topic_id)
    return f' im {board_label}'
