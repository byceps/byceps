"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.session.models.session_token \
    import SessionToken
from byceps.services.authorization.models import Role, UserRole
from byceps.services.consent import consent_service, \
    subject_service as consent_subject_service
from byceps.services.newsletter import service as newsletter_service
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope
from byceps.services.terms import version_service as terms_version_service
from byceps.services.user import event_service
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
        self.brand_id = self.brand.id

        self.setup_terms()
        self.setup_roles()

    def setup_terms(self):
        scope = Scope.for_brand(self.brand_id)

        snippet = snippet_service.create_fragment(
            scope, 'terms_of_service', self.admin.id,
            'Don\'t do anything stupid!')

        consent_subject = consent_subject_service.create_subject(
                '{}_terms-of-service_v1'.format(self.brand_id),
                'Terms of service for {} / v1'.format(self.brand.title),
                'terms_of_service')

        terms_version = terms_version_service.create_version(
            self.brand_id, '01-Jan-2016', snippet.id, consent_subject.id)

        self.terms_version_id = terms_version.id
        self.terms_consent_subject_id = terms_version.consent_subject_id

    def setup_roles(self):
        self.board_user_role = create_role('board_user')
        self.db.session.add(self.board_user_role)
        self.db.session.commit()

    @patch('byceps.email.send')
    def test_create(self, send_email_mock):
        user_count_before = get_user_count()

        form_data = {
            'screen_name': 'Hiro',
            'first_names': 'Hiroaki',
            'last_name': 'Protagonist',
            'email_address': 'hiro@metaverse.org',
            'password': 'Snow_Crash',
            'terms_version_id': self.terms_version_id,
            'consent_to_terms': 'y',
            'consent_to_privacy_policy': 'y',
            'subscribe_to_newsletter': 'y',
        }

        response = self.send_request(form_data)
        assert response.status_code == 302

        user_count_afterwards = get_user_count()
        assert user_count_afterwards == user_count_before + 1

        user = get_user(response)

        assert user.created_at is not None
        assert user.screen_name == 'Hiro'
        assert user.email_address == 'hiro@metaverse.org'
        assert not user.enabled
        assert not user.deleted

        # events
        assert_creation_event_created(user.id)

        # password
        assert_password_credentials_created(user.id)

        # session token
        assert_session_token_created(user.id)

        # avatar
        assert user.avatar is None

        # details
        assert user.detail.first_names == 'Hiroaki'
        assert user.detail.last_name == 'Protagonist'

        # authorization
        board_user_role = Role.query.get('board_user')
        actual_roles = get_user_roles(user.id)
        assert board_user_role in actual_roles

        # consents
        assert_consent(user.id, self.terms_consent_subject_id)

        # newsletter subscription
        assert is_subscribed_to_newsletter(user.id, self.brand_id)

        # confirmation e-mail

        verification_token = find_verification_token(user.id)
        assert verification_token is not None

        expected_sender = 'noreply@example.com'
        expected_recipients = ['hiro@metaverse.org']
        expected_subject = 'Hiro, bitte bestätige deine E-Mail-Adresse'
        expected_body = '''
Hallo Hiro,

bitte bestätige deine E-Mail-Adresse, indem du diese URL abrufst: http://example.com/users/email_address_confirmations/{}
        '''.strip().format(verification_token.token)

        send_email_mock.assert_called_once_with(
            expected_sender,
            expected_recipients,
            expected_subject,
            expected_body)

    @patch('byceps.email.send')
    def test_create_without_newsletter_subscription(self, send_email_mock):
        form_data = {
            'screen_name': 'Hiro',
            'first_names': 'Hiroaki',
            'last_name': 'Protagonist',
            'email_address': 'hiro@metaverse.org',
            'password': 'Snow_Crash',
            'terms_version_id': self.terms_version_id,
            'consent_to_terms': 'y',
            'consent_to_privacy_policy': 'y',
            'subscribe_to_newsletter': '',
        }

        response = self.send_request(form_data)
        assert response.status_code == 302

        user = get_user(response)

        # newsletter subscription
        assert not is_subscribed_to_newsletter(user.id, self.brand_id)

    # helpers

    def send_request(self, form_data):
        url = '/users/'

        with self.client() as client:
            return client.post(url, data=form_data)


def get_user(response):
    location = response.headers.get('Location')
    user_id = location.rpartition('/')[-1]
    return User.query.get(user_id)


def get_user_count():
    return User.query.count()


def get_user_roles(user_id):
    return Role.query \
        .join(UserRole) \
        .filter_by(user_id=user_id) \
        .all()


def find_verification_token(user_id):
    return verification_token_service \
        .find_for_email_address_confirmation_by_user(user_id)


def is_subscribed_to_newsletter(user_id, brand_id):
    return newsletter_service.is_subscribed(user_id, brand_id)


def assert_creation_event_created(user_id):
    events = event_service.get_events_of_type_for_user('user-created', user_id)
    assert len(events) == 1

    first_event = events[0]
    assert first_event.event_type == 'user-created'
    assert first_event.data == {}


def assert_password_credentials_created(user_id):
    credential = Credential.query.get(user_id)

    assert credential is not None
    assert credential.password_hash.startswith('pbkdf2:sha256:150000$')
    assert credential.updated_at is not None


def assert_session_token_created(user_id):
    session_token = SessionToken.query \
        .filter_by(user_id=user_id) \
        .one_or_none()

    assert session_token is not None
    assert session_token.token is not None
    assert session_token.created_at is not None


def assert_consent(user_id, subject_id):
    assert consent_service.has_user_consented_to_subject(user_id, subject_id)
