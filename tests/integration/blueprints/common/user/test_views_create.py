"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

import pytest

from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.session import service as session_service
from byceps.services.authorization import service as authorization_service
from byceps.services.brand import settings_service as brand_settings_service
from byceps.services.consent import (
    consent_service,
    subject_service as consent_subject_service,
)
from byceps.services.newsletter import (
    command_service as newsletter_command_service,
    service as newsletter_service,
)
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope
from byceps.services.terms import document_service as terms_document_service
from byceps.services.terms import version_service as terms_version_service
from byceps.services.user import event_service, service as user_service
from byceps.services.user.models.user import User
from byceps.services.verification_token.models import (
    Purpose as TokenPurpose,
    Token,
)

from tests.helpers import http_client


@pytest.fixture(scope='module')
def user_admin(make_user):
    return make_user('CommonUserAdmin')


@pytest.fixture(scope='module')
def terms_consent_subject_id(user_admin, brand):
    scope = Scope.for_brand(brand.id)

    snippet, _ = snippet_service.create_fragment(
        scope, 'terms_of_service', user_admin.id, 'Don\'t do anything stupid!'
    )

    consent_subject = consent_subject_service.create_subject(
        f'{brand.id}_terms-of-service_v1',
        f'Terms of service for {brand.title} / v1',
        'Ich akzeptiere die <a href="{url}" target="_blank">Allgemeinen Geschäftsbedingungen</a>.',
        '/terms/',
    )

    terms_document_id = brand.id
    terms_document = terms_document_service.create_document(
        terms_document_id, terms_document_id
    )

    terms_version = terms_version_service.create_version(
        terms_document.id, '01-Jan-2016', snippet.id, consent_subject.id
    )

    consent_subject_id = terms_version.consent_subject_id

    consent_subject_service.create_brand_requirement(
        brand.id, consent_subject_id
    )

    yield consent_subject_id

    consent_subject_service.delete_brand_requirement(
        brand.id, consent_subject_id
    )


@pytest.fixture(scope='module')
def privacy_policy_consent_subject_id(brand):
    consent_subject = consent_subject_service.create_subject(
        f'{brand.id}_privacy_policy_v1',
        f'Privacy policy for {brand.title} / v1',
        'Ich akzeptiere die <a href="{url}" target="_blank">Datenschutzbestimmungen</a>.',
        '/privacy',
    )

    consent_subject_service.create_brand_requirement(
        brand.id, consent_subject.id
    )

    yield consent_subject.id

    consent_subject_service.delete_brand_requirement(
        brand.id, consent_subject.id
    )


@pytest.fixture(scope='module')
def newsletter_list(brand):
    list_ = newsletter_command_service.create_list(brand.id, brand.title)

    name = 'newsletter_list_id'
    value = str(list_.id)

    brand_settings_service.create_setting(brand.id, name, value)

    yield

    brand_settings_service.remove_setting(brand.id, name)


@patch('byceps.email.send')
def test_create(
    send_email_mock,
    site_app,
    brand,
    site,
    terms_consent_subject_id,
    privacy_policy_consent_subject_id,
    newsletter_list,
):
    screen_name = 'Hiro'

    user_count_before = get_user_count()
    assert find_user(screen_name) is None

    form_data = {
        'screen_name': screen_name,
        'first_names': 'Hiroaki',
        'last_name': 'Protagonist',
        'email_address': 'hiro@metaverse.org',
        'password': 'Snow_Crash',
        f'consent_to_subject_{terms_consent_subject_id.hex}': 'y',
        f'consent_to_subject_{privacy_policy_consent_subject_id.hex}': 'y',
        'subscribe_to_newsletter': 'y',
    }

    response = send_request(site_app, form_data)
    assert response.status_code == 302

    user_count_afterwards = get_user_count()
    assert user_count_afterwards == user_count_before + 1

    user = find_user(screen_name)
    assert user is not None

    assert user.created_at is not None
    assert user.screen_name == 'Hiro'
    assert user.email_address == 'hiro@metaverse.org'
    assert not user.initialized
    assert not user.deleted

    # events
    assert_creation_event_created(user.id)

    # password
    assert_password_credentials_created(user.id)

    # Session token should not have been created at this point.
    session_token = session_service.find_session_token_for_user(user.id)
    assert session_token is None

    # avatar
    assert user.avatar is None

    # details
    assert user.detail.first_names == 'Hiroaki'
    assert user.detail.last_name == 'Protagonist'

    # authorization
    role_ids = authorization_service.find_role_ids_for_user(user.id)
    assert role_ids == set()

    # consents
    assert_consent(user.id, terms_consent_subject_id)
    assert_consent(user.id, privacy_policy_consent_subject_id)

    # newsletter subscription
    assert is_subscribed_to_newsletter(user.id, brand.id)

    # confirmation e-mail

    verification_token = find_verification_token(user.id)
    assert verification_token is not None

    expected_sender = 'noreply@acmecon.test'
    expected_recipients = ['hiro@metaverse.org']
    expected_subject = 'Hiro, bitte bestätige deine E-Mail-Adresse'
    expected_body = f'''
Hallo Hiro,

bitte bestätige deine E-Mail-Adresse, indem du diese URL abrufst: https://www.acmecon.test/users/email_address/confirmation/{verification_token.token}
    '''.strip()

    send_email_mock.assert_called_once_with(
        expected_sender, expected_recipients, expected_subject, expected_body
    )


@patch('byceps.email.send')
def test_create_without_newsletter_subscription(
    send_email_mock,
    site_app,
    brand,
    site,
    terms_consent_subject_id,
    privacy_policy_consent_subject_id,
    newsletter_list,
):
    screen_name = 'Hiro2'

    form_data = {
        'screen_name': screen_name,
        'first_names': 'Hiroaki',
        'last_name': 'Protagonist',
        'email_address': 'hiro2@metaverse.org',
        'password': 'Snow_Crash',
        f'consent_to_subject_{terms_consent_subject_id.hex}': 'y',
        f'consent_to_subject_{privacy_policy_consent_subject_id.hex}': 'y',
        'subscribe_to_newsletter': '',
    }

    response = send_request(site_app, form_data)
    assert response.status_code == 302

    user = find_user(screen_name)
    assert user is not None

    # newsletter subscription
    assert not is_subscribed_to_newsletter(user.id, brand.id)


# helpers


def send_request(app, form_data):
    url = '/users/'

    with http_client(app) as client:
        return client.post(url, data=form_data)


def find_user(screen_name):
    return user_service.find_user_by_screen_name(screen_name)


def get_user_count():
    return User.query.count()


def find_verification_token(user_id):
    return Token.query \
        .filter_by(user_id=user_id) \
        .for_purpose(TokenPurpose.email_address_confirmation) \
        .first()


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
    assert credential.password_hash.startswith('pbkdf2:sha256:250000$')
    assert credential.updated_at is not None


def assert_consent(user_id, subject_id):
    assert consent_service.has_user_consented_to_subject(user_id, subject_id)
