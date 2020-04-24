"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

import pytest

from byceps.services.authorization import service as authorization_service
from byceps.services.newsletter.models import (
    SubscriptionUpdate as DbSubscriptionUpdate,
)
from byceps.services.newsletter import command_service
from byceps.services.newsletter.types import SubscriptionState
from byceps.services.user import command_service as user_command_service

from tests.helpers import (
    create_permissions,
    create_role_with_permissions_assigned,
    create_user,
    http_client,
    login_user,
)


def test_export_subscribers(newsletter_list, subscribers, client):
    expected_data = {
        'subscribers': [
            {
                'screen_name': 'User-1',
                'email_address': 'user001@example.com',
            },

            # User #2 has declined a subscription, and thus should be
            # excluded.

            # User #3 is not initialized, and thus should be excluded.

            # User #4 has initially declined, but later requested a
            # subscription, so it should be included.
            {
                'screen_name': 'User-4',
                'email_address': 'user004@example.com',
            },

            # User #5 has initially requested, but later declined a
            # subscription, so it should be excluded.

            {
                'screen_name': 'User-6',
                'email_address': 'user006@example.com',
            },

            # User #7 has been suspended and should be excluded, regardless
            # of subscription state.

            # User #8 has been deleted and should be excluded, regardless
            # of subscription state.
        ],
    }

    url = f'/admin/newsletter/lists/{newsletter_list.id}/subscriptions/export'
    response = client.get(url)

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json == expected_data


def test_export_subscriber_email_addresses(newsletter_list, subscribers, client):
    expected_data = '\n'.join([
        'user001@example.com',
        # User #2 has declined a subscription.
        # User #3 is not initialized.
        # User #4 has initially declined, but later requested a subscription.
        'user004@example.com',
        # User #5 has initially requested, but later declined a subscription.
        'user006@example.com',
        # User #7 has been suspended, and thus should be excluded.
        # User #8 has been deleted, and thus should be excluded.
    ]).encode('utf-8')

    url = f'/admin/newsletter/lists/{newsletter_list.id}/subscriptions/email_addresses/export'
    response = client.get(url)

    assert response.status_code == 200
    assert response.content_type == 'text/plain; charset=utf-8'
    assert response.mimetype == 'text/plain'
    assert response.get_data() == expected_data


@pytest.fixture(scope='module')
def _newsletter_admin(make_user):
    yield from make_user('NewsletterAdmin')


@pytest.fixture(scope='module')
def newsletter_admin(_newsletter_admin):
    admin = _newsletter_admin

    permission_ids = {'admin.access', 'newsletter.export_subscribers'}
    role_id = 'newsletter_admin'
    create_permissions(permission_ids)
    create_role_with_permissions_assigned(role_id, permission_ids)
    authorization_service.assign_role_to_user(role_id, admin.id)

    login_user(admin.id)

    yield admin

    authorization_service.deassign_all_roles_from_user(admin.id, admin.id)
    authorization_service.delete_role(role_id)
    for permission_id in permission_ids:
        authorization_service.delete_permission(permission_id)

    user_command_service.delete_account(admin.id, admin.id, 'clean up')


@pytest.fixture(scope='module')
def newsletter_list(admin_app):
    newsletter_list = command_service.create_list('example', 'Example')
    yield newsletter_list
    command_service.delete_list(newsletter_list.id)


@pytest.fixture(scope='module')
def subscribers(db, newsletter_list):
    user_ids = []

    for number, initialized, suspended, deleted, states in [
        (1, True,  False, False, [SubscriptionState.requested                             ]),
        (2, True,  False, False, [SubscriptionState.declined                              ]),
        (3, False, False, False, [SubscriptionState.requested                             ]),
        (4, True,  False, False, [SubscriptionState.declined,  SubscriptionState.requested]),
        (5, True,  False, False, [SubscriptionState.requested, SubscriptionState.declined ]),
        (6, True,  False, False, [SubscriptionState.requested                             ]),
        (7, True,  True , False, [SubscriptionState.requested                             ]),
        (8, True,  False, True , [SubscriptionState.requested                             ]),
    ]:
        user = create_user(
            screen_name=f'User-{number:d}',
            email_address=f'user{number:03d}@example.com',
            initialized=initialized,
            suspended=suspended,
            deleted=deleted,
        )

        user_ids.append(user.id)

        add_subscriptions(db, user.id, newsletter_list.id, states)

    yield

    for user_id in user_ids:
        command_service.delete_subscription_updates(user_id, newsletter_list.id)
        user_command_service.delete_account(user_id, user_id, 'clean up')


def add_subscriptions(db, user_id, list_id, states):
    for state in states:
        # Timestamp must not be identical for multiple
        # `(user_id, list_id)` pairs.
        expressed_at = datetime.utcnow()

        subscription_update = DbSubscriptionUpdate(
            user_id, list_id, expressed_at, state
        )

        db.session.add(subscription_update)

    db.session.commit()


@pytest.fixture(scope='module')
def client(admin_app, newsletter_admin):
    """Provide a test HTTP client against the API."""
    with http_client(admin_app, user_id=newsletter_admin.id) as client:
        yield client
