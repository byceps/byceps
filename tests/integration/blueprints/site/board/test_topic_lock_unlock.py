"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.board import board_topic_command_service

from .helpers import find_topic


BASE_URL = 'http://www.acmecon.test'


def test_lock_topic(site_app, moderator, moderator_client, topic):
    topic_before = topic

    assert_topic_is_not_locked(topic_before)

    url = f'{BASE_URL}/board/topics/{topic_before.id}/flags/locked'
    response = moderator_client.post(url)

    assert response.status_code == 204

    db.session.expire_all()

    topic_afterwards = find_topic(topic_before.id)
    assert topic_afterwards is not None
    assert_topic_is_locked(topic_afterwards, moderator.id)


def test_unlock_topic(site_app, moderator, moderator_client, topic):
    topic_before = topic

    board_topic_command_service.lock_topic(topic_before.id, moderator)
    topic_before = find_topic(topic_before.id)
    assert topic_before is not None

    db.session.expire_all()

    assert_topic_is_locked(topic_before, moderator.id)

    url = f'{BASE_URL}/board/topics/{topic_before.id}/flags/locked'
    response = moderator_client.delete(url)

    assert response.status_code == 204

    db.session.expire_all()

    topic_afterwards = find_topic(topic_before.id)
    assert topic_afterwards is not None
    assert_topic_is_not_locked(topic_afterwards)


def assert_topic_is_locked(topic, moderator_id):
    assert topic.locked
    assert topic.locked_at is not None
    assert topic.locked_by.id == moderator_id


def assert_topic_is_not_locked(topic):
    assert not topic.locked
    assert topic.locked_at is None
    assert topic.locked_by is None
