"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.authz import (
    RoleAssignedToUserEvent,
    RoleDeassignedFromUserEvent,
)
from byceps.services.authz.models import RoleID

from .helpers import assert_text


def test_role_assigned_to_user_announced(
    app: Flask, now: datetime, make_event_user, webhook_for_irc
):
    expected_text = 'AuthzAdmin has assigned role "orga" to FreshOrga.'

    event = RoleAssignedToUserEvent(
        occurred_at=now,
        initiator=make_event_user(screen_name='AuthzAdmin'),
        user=make_event_user(screen_name='FreshOrga'),
        role_id=RoleID('orga'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_role_deassigned_from_user_announced(
    app: Flask, now: datetime, make_event_user, webhook_for_irc
):
    expected_text = (
        'AuthzAdmin has deassigned role "board_moderator" from FormerOrga.'
    )

    event = RoleDeassignedFromUserEvent(
        occurred_at=now,
        initiator=make_event_user(screen_name='AuthzAdmin'),
        user=make_event_user(screen_name='FormerOrga'),
        role_id=RoleID('board_moderator'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
