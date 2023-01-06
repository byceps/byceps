"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.newsletter import newsletter_command_service
from byceps.services.newsletter.types import SubscriptionState

from tests.helpers import log_in_user


def test_export_subscribers(newsletter_list, subscribers, client):
    expected_data = {
        'subscribers': [
            {
                'screen_name': 'User-1',
                'email_address': 'user001@users.test',
            },

            # User #2 has declined a subscription, and thus should be
            # excluded.

            # User #3 is not initialized, and thus should be excluded.

            # User #4 was initialized, but has its email address marked
            # as unverified later on, so it should be included.

            # User #5 has initially declined, but later requested a
            # subscription, so it should be included.
            {
                'screen_name': 'User-5',
                'email_address': 'user005@users.test',
            },

            # User #6 has initially requested, but later declined a
            # subscription, so it should be excluded.

            {
                'screen_name': 'User-7',
                'email_address': 'user007@users.test',
            },

            # User #8 has been suspended and should be excluded, regardless
            # of subscription state.

            # User #9 has been deleted and should be excluded, regardless
            # of subscription state.

            # Just another user to ensure the list hasn't been truncated early.
            {
                'screen_name': 'User-10',
                'email_address': 'user010@users.test',
            },
        ],
    }

    url = f'/admin/newsletter/lists/{newsletter_list.id}/subscriptions/export'
    response = client.get(url)

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json == expected_data


def test_export_subscriber_email_addresses(
    newsletter_list, subscribers, client
):
    expected_email_addresses = [
        'user001@users.test',
        # User #2 has declined a subscription.
        # User #3 is not initialized.
        # User #4 is initialized, but email address is unverified.
        # User #5 has initially declined, but later requested a subscription.
        'user005@users.test',
        # User #6 has initially requested, but later declined a subscription.
        'user007@users.test',
        # User #8 has been suspended, and thus should be excluded.
        # User #9 has been deleted, and thus should be excluded.
        'user010@users.test',
    ]
    expected_data = '\n'.join(expected_email_addresses).encode('utf-8')

    url = f'/admin/newsletter/lists/{newsletter_list.id}/subscriptions/email_addresses/export'
    response = client.get(url)

    assert response.status_code == 200
    assert response.content_type == 'text/plain; charset=utf-8'
    assert response.mimetype == 'text/plain'
    assert response.get_data() == expected_data


@pytest.fixture(scope='package')
def newsletter_admin(make_admin):
    permission_ids = {'admin.access', 'newsletter.export_subscribers'}
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='module')
def newsletter_list(admin_app):
    return newsletter_command_service.create_list('example', 'Example')


@pytest.fixture(scope='module')
def subscribers(make_user, newsletter_list):
    for (
        number,
        initialized,
        email_address_verified,
        suspended,
        deleted,
        states,
    ) in [
        ( 1, True , True , False, False, [SubscriptionState.requested                             ]),
        ( 2, True , True , False, False, [SubscriptionState.declined                              ]),
        ( 3, False, True , False, False, [SubscriptionState.requested                             ]),
        ( 4, True , False, False, False, [SubscriptionState.requested                             ]),
        ( 5, True , True , False, False, [SubscriptionState.declined,  SubscriptionState.requested]),
        ( 6, True , True , False, False, [SubscriptionState.requested, SubscriptionState.declined ]),
        ( 7, True , True , False, False, [SubscriptionState.requested                             ]),
        ( 8, True , True , True , False, [SubscriptionState.requested                             ]),
        ( 9, True , True , False, True , [SubscriptionState.requested                             ]),
        (10, True , True , False, False, [SubscriptionState.requested                             ]),
    ]:
        user = make_user(
            screen_name=f'User-{number:d}',
            email_address=f'user{number:03d}@users.test',
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
                )
            elif state == SubscriptionState.declined:
                newsletter_command_service.unsubscribe(
                    user.id, list_id, expressed_at
                )


@pytest.fixture(scope='package')
def client(admin_app, make_client, newsletter_admin):
    return make_client(admin_app, user_id=newsletter_admin.id)
