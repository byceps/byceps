"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.session.models import SessionToken
from byceps.services.authorization.models import Role, UserRole
from byceps.services.terms.models.version import Version as TermsVersion
from byceps.services.terms import service as terms_service
from byceps.services.user.models.user import User
from byceps.services.verification_token import service as \
    verification_token_service

from tests.base import AbstractAppTestCase

from testfixtures.authorization import create_role


class UserCreateTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.admin = self.create_user('Admin')

        self.create_brand_and_party()
        self.set_brand_email_sender_address(self.brand.id, 'noreply@example.com')

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

    @patch('byceps.email.send')
    def test_create(self, send_email_mock):
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

        assert response.status_code == 302

        user_count_afterwards = self.get_user_count()
        assert user_count_afterwards == user_count_before + 1

        location = response.headers.get('Location')
        user_id = location.rpartition('/')[-1]
        user = User.query.get(user_id)

        assert user.created_at is not None
        assert user.screen_name == 'Hiro'
        assert user.email_address == 'hiro@metaverse.org'
        assert not user.enabled
        assert not user.deleted

        # password
        credential = Credential.query.get(user.id)
        assert credential is not None
        assert credential.password_hash.startswith('pbkdf2:sha256:100000$')
        assert credential.updated_at is not None

        # session token
        session_token = SessionToken.query \
            .filter_by(user_id=user.id) \
            .one_or_none()
        assert session_token is not None
        assert session_token.token is not None
        assert session_token.created_at is not None

        # avatar
        assert user.avatar is None

        # details
        assert user.detail.first_names == 'Hiroaki'
        assert user.detail.last_name == 'Protagonist'

        # authorization
        board_user_role = Role.query.get('board_user')
        actual_roles = Role.query \
            .join(UserRole) \
            .filter_by(user_id=user.id) \
            .all()
        assert board_user_role in actual_roles

        # consent to terms of service
        terms_consents = terms_service.get_consents_by_user(user.id)
        assert len(terms_consents) == 1
        assert terms_consents[0].version_id == self.terms_version_id

        # confirmation e-mail

        verification_token = verification_token_service \
            .find_for_email_address_confirmation_by_user(user.id)
        assert verification_token is not None

        expected_sender = 'noreply@example.com'
        expected_recipients = ['hiro@metaverse.org']
        expected_subject = 'Hiro, bitte bestätige deine E-Mail-Adresse'
        expected_body = '''
Hallo Hiro,

bitte bestätige deine E-Mail-Adresse indem du diese URL abrufst: http://example.com/users/email_address_confirmations/{}
        '''.strip().format(verification_token.token)

        send_email_mock.assert_called_once_with(
            expected_sender,
            expected_recipients,
            expected_subject,
            expected_body)

    # helpers

    def get_user_count(self):
        return User.query.count()

    def send_request(self, form_data):
        url = '/users/'

        with self.client() as client:
            return client.post(url, data=form_data)

