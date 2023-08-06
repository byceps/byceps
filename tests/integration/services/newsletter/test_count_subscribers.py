"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.newsletter import (
    newsletter_command_service,
    newsletter_service,
)
from byceps.services.newsletter.types import SubscriptionState

from tests.helpers import generate_token


def test_count_subscribers(newsletter_list, subscribers):
    # Included users:
    # - #1
    # - #5 (eventually requested subscription)
    # - #7
    # Excluded users:
    # - #2 (declined subscription)
    # - #3 (not initialized)
    # - #4 (unverified email address)
    # - #6 (eventually declined subscription)
    # - #8 (suspended)
    # - #9 (deleted)
    expected = 3

    actual = newsletter_service.count_subscribers(newsletter_list.id)

    assert actual == expected


@pytest.fixture(scope='module')
def newsletter_list(admin_app):
    list_id = generate_token()
    return newsletter_command_service.create_list(list_id, list_id)


@pytest.fixture(scope='module')
def subscribers(make_user, newsletter_list):
    for initialized, email_address_verified, suspended, deleted, states in [
        (True , True , False, False, [SubscriptionState.requested                             ]),  # 1
        (True , True , False, False, [SubscriptionState.declined                              ]),  # 2
        (False, True , False, False, [SubscriptionState.requested                             ]),  # 3
        (True , False, False, False, [SubscriptionState.requested                             ]),  # 4
        (True , True , False, False, [SubscriptionState.declined,  SubscriptionState.requested]),  # 5
        (True , True , False, False, [SubscriptionState.requested, SubscriptionState.declined ]),  # 6
        (True , True , False, False, [SubscriptionState.requested                             ]),  # 7
        (True , True , True , False, [SubscriptionState.requested                             ]),  # 8
        (True , True , False, True , [SubscriptionState.requested                             ]),  # 9
    ]:
        user = make_user(
            email_address_verified=email_address_verified,
            initialized=initialized,
            suspended=suspended,
            deleted=deleted,
        )

        list_id = newsletter_list.id

        for state in states:
            # Timestamp must not be identical for multiple
            # `(user_id, list_id)` pairs.
            expressed_at = datetime.utcnow()

            if state == SubscriptionState.requested:
                newsletter_command_service.subscribe(
                    user.id, list_id, expressed_at
                ).unwrap()
            elif state == SubscriptionState.declined:
                newsletter_command_service.unsubscribe(
                    user.id, list_id, expressed_at
                ).unwrap()
