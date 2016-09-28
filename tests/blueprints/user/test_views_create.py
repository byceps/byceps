# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.terms.models import Version as TermsVersion
from byceps.blueprints.user.models.user import User
from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.session.models import SessionToken

from tests.base import AbstractAppTestCase

from testfixtures.authorization import create_role
from testfixtures.user import create_user


class UserCreateTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.setup_terms()
        self.setup_roles()

    def setup_terms(self):
        self.terms_version = TermsVersion(self.brand.id, self.admin.id, 'ToS')
        self.db.session.add(self.terms_version)
        self.db.session.commit()

    def setup_roles(self):
        self.board_user_role = create_role('board_user')
        self.db.session.add(self.board_user_role)
        self.db.session.commit()

    def test_create(self):
        user_count_before = self.get_user_count()

        form_data = {
            'screen_name': 'Hiro',
            'first_names': 'Hiroaki',
            'last_name': 'Protagonist',
            'email_address': 'hiro@metaverse.org',
            'password': 'Snow_Crash',
            'consent_to_terms': 'y',
        }

        response = self.send_request(form_data)

        self.assertEqual(response.status_code, 302)

        user_count_afterwards = self.get_user_count()
        self.assertEqual(user_count_afterwards, user_count_before + 1)

        location = response.headers.get('Location')
        user_id = location.rpartition('/')[-1]
        user = User.query.get(user_id)

        self.assertIsNotNone(user.created_at)
        self.assertEqual(user.screen_name, 'Hiro')
        self.assertEqual(user.email_address, 'hiro@metaverse.org')
        self.assertFalse(user.enabled)
        self.assertFalse(user.deleted)

        # password
        credential = Credential.query.get(user.id)
        self.assertIsNotNone(credential)
        self.assertTrue(credential.password_hash.startswith('pbkdf2:sha256:100000$'))
        self.assertIsNotNone(credential.updated_at)

        # session token
        session_token = SessionToken.query \
            .filter_by(user_id=user.id) \
            .one_or_none()
        self.assertIsNotNone(session_token)
        self.assertIsNotNone(session_token.token)
        self.assertIsNotNone(session_token.created_at)

        # avatar
        self.assertIsNone(user.avatar)

        # details
        self.assertEqual(user.detail.first_names, 'Hiroaki')
        self.assertEqual(user.detail.last_name, 'Protagonist')

    # helpers

    def get_user_count(self):
        return User.query.count()

    def send_request(self, form_data):
        url = '/users/'

        with self.client() as client:
            return client.post(url, data=form_data)

