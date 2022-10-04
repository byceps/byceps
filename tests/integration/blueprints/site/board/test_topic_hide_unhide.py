"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.board import board_topic_command_service

from .helpers import find_topic


def test_hide_topic(site_app, moderator, moderator_client, topic):
    topic_before = topic

    assert_topic_is_not_hidden(topic_before)

    url = f'/board/topics/{topic_before.id}/flags/hidden'
    response = moderator_client.post(url)

    assert response.status_code == 204
    topic_afterwards = find_topic(topic_before.id)
    assert_topic_is_hidden(topic_afterwards, moderator.id)


def test_unhide_topic(site_app, moderator, moderator_client, topic):
    topic_before = topic

    board_topic_command_service.hide_topic(topic_before.id, moderator.id)

    assert_topic_is_hidden(topic_before, moderator.id)

    url = f'/board/topics/{topic_before.id}/flags/hidden'
    response = moderator_client.delete(url)

    assert response.status_code == 204
    topic_afterwards = find_topic(topic_before.id)
    assert_topic_is_not_hidden(topic_afterwards)


def assert_topic_is_hidden(topic, moderator_id):
    assert topic.hidden
    assert topic.hidden_at is not None
    assert topic.hidden_by_id == moderator_id


def assert_topic_is_not_hidden(topic):
    assert not topic.hidden
    assert topic.hidden_at is None
    assert topic.hidden_by_id is None
