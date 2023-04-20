"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.announce.connections import build_announcement_request
from byceps.events.board import BoardPostingCreated, BoardTopicCreated
from byceps.services.board import (
    board_category_command_service,
    board_posting_command_service,
    board_topic_command_service,
)
from byceps.services.board.models import BoardID
from byceps.services.webhooks.models import OutgoingWebhook

from .helpers import build_announcement_request_for_discord, build_webhook


def test_announce_topic_created(admin_app, board, topic, creator):
    expected_url = f'https://website.test/board/topics/{topic.id}'
    expected_content = (
        '[Forum] RocketRandy hat das Thema '
        '"Cannot connect to the party network :(" erstellt: '
        f'<{expected_url}>'
    )
    expected = build_announcement_request_for_discord(expected_content)

    event = BoardTopicCreated(
        occurred_at=topic.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        board_id=board.id,
        topic_id=topic.id,
        topic_creator_id=creator.id,
        topic_creator_screen_name=creator.screen_name,
        topic_title=topic.title,
        url=expected_url,
    )

    webhook = build_board_webhook(board.id)

    assert build_announcement_request(event, webhook) == expected


def test_announce_posting_created(admin_app, board, posting, creator):
    expected_url = f'https://website.test/board/postings/{posting.id}'
    expected_content = (
        '[Forum] RocketRandy hat auf das Thema '
        '"Cannot connect to the party network :(" geantwortet: '
        f'<{expected_url}>'
    )
    expected = build_announcement_request_for_discord(expected_content)

    event = BoardPostingCreated(
        occurred_at=posting.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        board_id=board.id,
        posting_creator_id=creator.id,
        posting_creator_screen_name=creator.screen_name,
        posting_id=posting.id,
        topic_id=posting.topic.id,
        topic_title=posting.topic.title,
        topic_muted=posting.topic.muted,
        url=expected_url,
    )

    webhook = build_board_webhook(board.id)

    assert build_announcement_request(event, webhook) == expected


# helpers


def build_board_webhook(board_id: BoardID) -> OutgoingWebhook:
    return build_webhook(
        event_types={
            'board-posting-created',
            'board-topic-created',
        },
        event_filters={
            'board-posting-created': {'board_id': [str(board_id)]},
            'board-topic-created': {'board_id': [str(board_id)]},
        },
        text_prefix='[Forum] ',
        url='https://webhoooks.test/board',
    )


@pytest.fixture(scope='module')
def creator(make_user):
    return make_user('RocketRandy')


@pytest.fixture(scope='module')
def category(board):
    slug = 'support'
    title = 'Support'
    description = 'How can I help you, dear Sir/Madam?'

    return board_category_command_service.create_category(
        board.id, slug, title, description
    )


@pytest.fixture(scope='module')
def topic(category, creator):
    title = 'Cannot connect to the party network :('
    body = 'I think I did not receive an IP address via DHCP. BUT WHY?!'

    topic, _ = board_topic_command_service.create_topic(
        category.id, creator.id, title, body
    )

    return topic


@pytest.fixture(scope='module')
def posting(topic, creator):
    posting, _ = board_posting_command_service.create_posting(
        topic.id, creator.id, 'This is nice and all, but check out my website!'
    )

    return posting
