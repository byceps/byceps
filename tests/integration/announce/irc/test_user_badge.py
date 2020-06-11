"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.announce.irc import user_badge  # Load signal handlers.
from byceps.blueprints.user_badge import signals
from byceps.services.user_badge import command_service as badge_command_service

from .helpers import assert_submitted_data, CHANNEL_ORGA_LOG, mocked_irc_bot


EXPECTED_CHANNELS = [CHANNEL_ORGA_LOG]


def test_user_badge_awarding_announced_without_initiator(app, make_user):
    expected_text = (
        'Jemand hat das Abzeichen "First Post!" an Erster verliehen.'
    )

    badge = badge_command_service.create_badge(
        'first-post', 'First Post!', 'first-post.svg'
    )

    user = make_user('Erster')

    _, event = badge_command_service.award_badge_to_user(badge.id, user.id)

    with mocked_irc_bot() as mock:
        signals.user_badge_awarded.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)


def test_user_badge_awarding_announced_with_initiator(
    app, make_user, admin_user
):
    expected_text = (
        'Admin hat das Abzeichen "Glanzleistung" an PathFinder verliehen.'
    )

    badge = badge_command_service.create_badge(
        'glnzlstng', 'Glanzleistung', 'glanz.svg'
    )

    user = make_user('PathFinder')

    _, event = badge_command_service.award_badge_to_user(
        badge.id, user.id, initiator_id=admin_user.id
    )

    with mocked_irc_bot() as mock:
        signals.user_badge_awarded.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)
