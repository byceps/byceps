"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.tourney import (
    tourney_match_comment_service,
    tourney_match_service,
)


def test_hide_comment(api_client, api_client_authz_header, admin_user, comment):
    comment_before = tourney_match_comment_service.get_comment(comment.id)
    assert not comment_before.hidden
    assert comment_before.hidden_at is None
    assert comment_before.hidden_by is None

    url = f'/api/v1/tourney/match_comments/{comment.id}/flags/hidden'
    headers = [api_client_authz_header]
    json_data = {'initiator_id': str(admin_user.id)}

    response = api_client.post(url, headers=headers, json=json_data)
    assert response.status_code == 204

    comment_after = tourney_match_comment_service.get_comment(comment.id)
    assert comment_after.hidden
    assert comment_after.hidden_at is not None
    assert comment_after.hidden_by is not None
    assert comment_after.hidden_by.id == admin_user.id


def test_unhide_comment(
    api_client, api_client_authz_header, admin_user, comment
):
    tourney_match_comment_service.hide_comment(comment.id, admin_user.id)

    comment_before = tourney_match_comment_service.get_comment(comment.id)
    assert comment_before.hidden
    assert comment_before.hidden_at is not None
    assert comment_before.hidden_by is not None

    url = f'/api/v1/tourney/match_comments/{comment.id}/flags/hidden'
    headers = [api_client_authz_header]
    json_data = {'initiator_id': str(admin_user.id)}

    response = api_client.delete(url, headers=headers, json=json_data)
    assert response.status_code == 204

    comment_after = tourney_match_comment_service.get_comment(comment.id)
    assert not comment_after.hidden
    assert comment_after.hidden_at is None
    assert comment_after.hidden_by is None


# helpers


@pytest.fixture
def match(api_app, scope='module'):
    return tourney_match_service.create_match()


@pytest.fixture
def comment(api_app, match, user):
    return tourney_match_comment_service.create_comment(
        match.id, user.id, '¡Vámonos!'
    )
