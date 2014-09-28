# -*- coding: utf-8 -*-

import json

from byceps.blueprints.authorization.models import Permission, Role
from byceps.blueprints.brand.models import Brand
from byceps.blueprints.newsletter_admin.authorization import NewsletterPermission
from byceps.blueprints.newsletter.models import Subscription, SubscriptionState
from byceps.blueprints.user.models import User

from tests import AbstractAppTestCase


class NewsletterAdminTestCase(AbstractAppTestCase):

    def setUp(self):
        super(NewsletterAdminTestCase, self).setUp(env='test_admin')

        self.setUp_current_user()

        self.user1 = self.create_user(1)
        self.user2 = self.create_user(2)
        self.user3 = self.create_user(3)
        self.db.session.commit()

    def setUp_current_user(self):
        export_subscribers_permission = Permission.from_enum_member(
            NewsletterPermission.export_subscribers)
        self.db.session.add(export_subscribers_permission)

        newsletter_admin_role = Role(id='newsletter_admin')
        self.db.session.add(newsletter_admin_role)

        newsletter_admin_role.permissions.append(export_subscribers_permission)

        self.current_user = self.create_user(99, enabled=True)
        self.current_user.roles.add(newsletter_admin_role)

        self.db.session.commit()

    def test_export_subscribers(self):
        expected_data = {
            'subscribers': [
                {
                    'screen_name': 'User-1',
                    'email_address': 'user001@example.com',
                },
                {
                    'screen_name': 'User-3',
                    'email_address': 'user003@example.com',
                },
            ],
        }

        self.add_subscription(self.user1, SubscriptionState.requested)
        self.add_subscription(self.user2, SubscriptionState.declined)
        self.add_subscription(self.user3, SubscriptionState.requested)
        self.db.session.commit()

        url = '/admin/newsletter/subscriptions/{}/export'.format(self.brand.id)
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data, expected_data)

    def create_user(self, number, *, enabled=True):
        screen_name = 'User-{:d}'.format(number)
        email_address = 'user{:03d}@example.com'.format(number)
        user = User.create(screen_name, email_address, 'le_password')
        user.enabled = enabled
        self.db.session.add(user)
        return user

    def add_subscription(self, user, state):
        subscription = Subscription(user, state, brand=self.brand)
        self.db.session.add(subscription)
