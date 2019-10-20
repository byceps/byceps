"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.board import (
    posting_command_service as board_posting_command_service,
)

from ...helpers import http_client

from .helpers import find_posting


@pytest.fixture
def moderator(make_moderator):
    return make_moderator('board.hide')


def test_hide_posting(party_app_with_db, moderator, posting):
    posting_before = posting

    assert_posting_is_not_hidden(posting_before)

    url = f'/board/postings/{posting_before.id}/flags/hidden'
    with http_client(party_app_with_db, user_id=moderator.id) as client:
        response = client.post(url)

    assert response.status_code == 204
    posting_afterwards = find_posting(posting_before.id)
    assert_posting_is_hidden(posting_afterwards, moderator.id)


def test_unhide_posting(party_app_with_db, moderator, posting):
    posting_before = posting

    board_posting_command_service.hide_posting(posting_before.id, moderator.id)

    assert_posting_is_hidden(posting_before, moderator.id)

    url = f'/board/postings/{posting_before.id}/flags/hidden'
    with http_client(party_app_with_db, user_id=moderator.id) as client:
        response = client.delete(url)

    assert response.status_code == 204
    posting_afterwards = find_posting(posting_before.id)
    assert_posting_is_not_hidden(posting_afterwards)


def assert_posting_is_hidden(posting, moderator_id):
    assert posting.hidden
    assert posting.hidden_at is not None
    assert posting.hidden_by_id == moderator_id


def assert_posting_is_not_hidden(posting):
    assert not posting.hidden
    assert posting.hidden_at is None
    assert posting.hidden_by_id is None
