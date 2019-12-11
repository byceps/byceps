"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.tourney import match_comment_service, match_service


def test_hide_comment(api_client, api_client_authz_header, admin, comment):
    comment_before = match_comment_service.find_comment(comment.id)
    assert not comment_before.hidden
    assert comment_before.hidden_at is None
    assert comment_before.hidden_by_id is None

    url = f'/api/tourney/match_comments/{comment.id}/flags/hidden'
    headers = [api_client_authz_header]
    json_data = {'initiator_id': str(admin.id)}

    response = api_client.post(url, headers=headers, json=json_data)
    assert response.status_code == 204

    comment_after = match_comment_service.find_comment(comment.id)
    assert comment_after.hidden
    assert comment_after.hidden_at is not None
    assert comment_after.hidden_by_id == admin.id


def test_unhide_comment(api_client, api_client_authz_header, admin, comment):
    match_comment_service.hide_comment(comment.id, admin.id)

    comment_before = match_comment_service.find_comment(comment.id)
    assert comment_before.hidden
    assert comment_before.hidden_at is not None
    assert comment_before.hidden_by_id is not None

    url = f'/api/tourney/match_comments/{comment.id}/flags/hidden'
    headers = [api_client_authz_header]
    json_data = {'initiator_id': str(admin.id)}

    response = api_client.delete(url, headers=headers, json=json_data)
    assert response.status_code == 204

    comment_after = match_comment_service.find_comment(comment.id)
    assert not comment_after.hidden
    assert comment_after.hidden_at is None
    assert comment_after.hidden_by_id is None


# helpers


@pytest.fixture
def match(app, scope='module'):
    return match_service.create_match()


@pytest.fixture
def comment(app, match, user):
    return match_comment_service.create_comment(match.id, user.id, '¡Vámonos!')
