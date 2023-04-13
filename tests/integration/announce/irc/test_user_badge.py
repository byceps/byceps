"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.announce.connections import build_announcement_request
from byceps.services.user_badge import (
    user_badge_awarding_service,
    user_badge_service,
)

from .helpers import build_announcement_request_for_irc


def test_user_badge_awarding_announced_without_initiator(
    admin_app, make_user, webhook_for_irc
):
    expected_text = (
        'Jemand hat das Abzeichen "First Post!" an Erster verliehen.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    badge = user_badge_service.create_badge(
        'first-post', 'First Post!', 'first-post.svg'
    )

    user = make_user('Erster')

    _, event = user_badge_awarding_service.award_badge_to_user(
        badge.id, user.id
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_user_badge_awarding_announced_with_initiator(
    admin_app, make_user, admin_user, webhook_for_irc
):
    expected_text = (
        'Admin hat das Abzeichen "Glanzleistung" an PathFinder verliehen.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    badge = user_badge_service.create_badge(
        'glnzlstng', 'Glanzleistung', 'glanz.svg'
    )

    user = make_user('PathFinder')

    _, event = user_badge_awarding_service.award_badge_to_user(
        badge.id, user.id, initiator_id=admin_user.id
    )

    assert build_announcement_request(event, webhook_for_irc) == expected
