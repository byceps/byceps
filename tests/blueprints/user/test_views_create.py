"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.session.models import SessionToken
from byceps.services.authorization.models import Role, UserRole
from byceps.services.terms.models import Version as TermsVersion
from byceps.services.terms import service as terms_service
from byceps.services.user.models.user import User

from tests.base import AbstractAppTestCase

from testfixtures.authorization import create_role


class UserCreateTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.setup_terms()
        self.setup_roles()

    def setup_terms(self):
        terms_version = TermsVersion(self.brand.id, self.admin.id,
                                     '01-Jan-2016', 'ToS')

        self.db.session.add(terms_version)
        self.db.session.commit()

        self.terms_version_id = terms_version.id

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
            'terms_version_id': self.terms_version_id,
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

        # authorization
        board_user_role = Role.query.get('board_user')
        actual_roles = Role.query \
            .join(UserRole) \
            .filter_by(user_id=user.id) \
            .all()
        self.assertIn(board_user_role, actual_roles)

        # consent to terms of service
        terms_consents = terms_service.get_consents_by_user(user.id)
        self.assertEqual(len(terms_consents), 1)
        self.assertEqual(terms_consents[0].version_id, self.terms_version_id)

    # helpers

    def get_user_count(self):
        return User.query.count()

    def send_request(self, form_data):
        url = '/users/'

        with self.client() as client:
            return client.post(url, data=form_data)

