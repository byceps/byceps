# -*- coding: utf-8 -*-

import json

from byceps.blueprints.authorization.models import Permission, Role
from byceps.blueprints.newsletter_admin.authorization import NewsletterPermission
from byceps.blueprints.newsletter.models import Subscription, SubscriptionState
from byceps.blueprints.user.models import User

from tests import AbstractAppTestCase


class NewsletterAdminTestCase(AbstractAppTestCase):

    def setUp(self):
        super(NewsletterAdminTestCase, self).setUp(env='test_admin')

        self.setup_current_user()
        self.setup_subscribers()

    def setup_current_user(self):
        export_subscribers_permission = Permission.from_enum_member(
            NewsletterPermission.export_subscribers)
        self.db.session.add(export_subscribers_permission)

        newsletter_admin_role = Role(id='newsletter_admin')
        self.db.session.add(newsletter_admin_role)

        newsletter_admin_role.permissions.append(export_subscribers_permission)

        self.current_user = self.create_user(99, enabled=True)
        self.current_user.roles.add(newsletter_admin_role)

        self.db.session.commit()

    def setup_subscribers(self):
        for user_number, enabled, states in [
            (1, True,  [SubscriptionState.requested                             ]),
            (2, True,  [SubscriptionState.declined                              ]),
            (3, False, [SubscriptionState.requested                             ]),
            (4, True,  [SubscriptionState.declined,  SubscriptionState.requested]),
            (5, True,  [SubscriptionState.requested, SubscriptionState.declined ]),
            (6, True,  [SubscriptionState.requested                             ]),
        ]:
            user = self.create_user(user_number, enabled=enabled)
            self.add_subscriptions(user, states)

        self.db.session.commit()

    def test_export_subscribers(self):
        expected_data = {
            'subscribers': [
                {
                    'screen_name': 'User-1',
                    'email_address': 'user001@example.com',
                },
                # User #2 has declined a subscription.
                # User #3 is not enabled.
                # User #4 has initially declined, but later requested a subscription.
                {
                    'screen_name': 'User-4',
                    'email_address': 'user004@example.com',
                },
                # User #5 has initially requested, but later declined a subscription.
                {
                    'screen_name': 'User-6',
                    'email_address': 'user006@example.com',
                },
            ],
        }

        url = '/admin/newsletter/subscriptions/{}/export'.format(self.brand.id)
        response = self.get_with_current_user(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data, expected_data)

    def test_export_subscriber_email_addresses(self):
        expected_data = '\n'.join([
            'user001@example.com',
            # User #2 has declined a subscription.
            # User #3 is not enabled.
            # User #4 has initially declined, but later requested a subscription.
            'user004@example.com',
            # User #5 has initially requested, but later declined a subscription.
            'user006@example.com',
        ]).encode('utf-8')

        url = '/admin/newsletter/subscriptions/{}/export_email_addresses'.format(self.brand.id)
        response = self.get_with_current_user(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/plain; charset=utf-8')
        self.assertEqual(response.mimetype, 'text/plain')
        self.assertEqual(response.data, expected_data)

    def create_user(self, number, *, enabled=True):
        screen_name = 'User-{:d}'.format(number)
        email_address = 'user{:03d}@example.com'.format(number)
        user = User.create(screen_name, email_address, 'le_password')
        user.enabled = enabled
        self.db.session.add(user)
        return user

    def add_subscriptions(self, user, states):
        for state in states:
            self.add_subscription(user, state)

    def add_subscription(self, user, state):
        subscription = Subscription(user, state, brand=self.brand)
        self.db.session.add(subscription)

    def get_with_current_user(self, url):
        """Make a GET request as the current user and return the response."""
        self.enrich_session_for_user(self.current_user)
        return self.client.get(url)
