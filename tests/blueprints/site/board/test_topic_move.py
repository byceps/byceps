"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.helpers import http_client

from .helpers import create_category, create_topic, find_topic


def test_move_topic(party_app_with_db, make_moderator, normal_user, board):
    moderator = make_moderator('board_topic.move')

    category_id_1 = create_category(board.id, number=1).id
    category_id_2 = create_category(board.id, number=2).id

    topic_before = create_topic(category_id_1, normal_user.id)
    assert topic_before.category.id == category_id_1

    url = f'/board/topics/{topic_before.id}/move'
    form_data = {'category_id': category_id_2}
    with http_client(party_app_with_db, user_id=moderator.id) as client:
        response = client.post(url, data=form_data)

    assert response.status_code == 302

    topic_afterwards = find_topic(topic_before.id)
    assert topic_afterwards.category.id == category_id_2
