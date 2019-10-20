"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.board import (
    topic_command_service as board_topic_command_service,
)

from ...helpers import http_client

from .helpers import find_topic


@pytest.fixture
def moderator(make_moderator):
    return make_moderator('board_topic.pin')


def test_pin_topic(party_app_with_db, moderator, topic):
    topic_before = topic

    assert_topic_is_not_pinned(topic_before)

    url = f'/board/topics/{topic_before.id}/flags/pinned'
    with http_client(party_app_with_db, user_id=moderator.id) as client:
        response = client.post(url)

    assert response.status_code == 204
    topic_afterwards = find_topic(topic_before.id)
    assert_topic_is_pinned(topic_afterwards, moderator.id)


def test_unpin_topic(party_app_with_db, moderator, topic):
    topic_before = topic
    board_topic_command_service.pin_topic(topic_before.id, moderator.id)

    assert_topic_is_pinned(topic_before, moderator.id)

    url = f'/board/topics/{topic_before.id}/flags/pinned'
    with http_client(party_app_with_db, user_id=moderator.id) as client:
        response = client.delete(url)

    assert response.status_code == 204
    topic_afterwards = find_topic(topic_before.id)
    assert_topic_is_not_pinned(topic_afterwards)


def assert_topic_is_pinned(topic, moderator_id):
    assert topic.pinned
    assert topic.pinned_at is not None
    assert topic.pinned_by_id == moderator_id


def assert_topic_is_not_pinned(topic):
    assert not topic.pinned
    assert topic.pinned_at is None
    assert topic.pinned_by_id is None
