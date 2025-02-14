"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

import pytest
from sqlalchemy import select

from byceps.database import db
from byceps.services.authn.password.dbmodels import DbCredential
from byceps.services.authn.session import authn_session_service
from byceps.services.authz import authz_service
from byceps.services.brand import brand_service
from byceps.services.consent import (
    brand_requirements_service,
    consent_service,
    consent_subject_service,
)
from byceps.services.newsletter import (
    newsletter_command_service,
    newsletter_service,
)
from byceps.services.user import user_log_service, user_service
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.verification_token.dbmodels import DbVerificationToken
from byceps.services.verification_token.models import Purpose as TokenPurpose

from tests.helpers import http_client


@pytest.fixture(scope='module')
def terms_consent_subject_id(brand):
    consent_subject = consent_subject_service.create_subject(
        f'{brand.id}_terms-of-service_v1',
        f'Terms of service for {brand.title} / v1',
        'Ich akzeptiere die <a href="{url}" target="_blank">Allgemeinen Geschäftsbedingungen</a>.',
        '/terms/',
    )

    brand_requirements_service.create_brand_requirement(
        brand.id, consent_subject.id
    )

    yield consent_subject.id

    brand_requirements_service.delete_brand_requirement(
        brand.id, consent_subject.id
    )


@pytest.fixture(scope='module')
def privacy_policy_consent_subject_id(brand):
    consent_subject = consent_subject_service.create_subject(
        f'{brand.id}_privacy_policy_v1',
        f'Privacy policy for {brand.title} / v1',
        'Ich akzeptiere die <a href="{url}" target="_blank">Datenschutzbestimmungen</a>.',
        '/privacy',
    )

    brand_requirements_service.create_brand_requirement(
        brand.id, consent_subject.id
    )

    yield consent_subject.id

    brand_requirements_service.delete_brand_requirement(
        brand.id, consent_subject.id
    )


@pytest.fixture(scope='module')
def newsletter_list(brand):
    list_ = newsletter_command_service.create_list(brand.id, brand.title)

    brand_service.set_newsletter_list_for_brand(brand.id, list_.id)

    yield

    brand_service.unset_newsletter_list_for_brand(brand.id, list_.id)


@patch('byceps.services.email.email_service.send')
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
        'first_name': 'Hiroaki',
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

    # log entries
    assert_creation_log_entry_created(user.id, site.id)

    # password
    assert_password_credentials_created(user.id)

    # Session token should not have been created at this point.
    session_token = authn_session_service.find_session_token_for_user(user.id)
    assert session_token is None

    # avatar
    assert user.avatar is None

    # details
    assert user.detail.first_name == 'Hiroaki'
    assert user.detail.last_name == 'Protagonist'

    # authorization
    role_ids = authz_service.find_role_ids_for_user(user.id)
    assert role_ids == set()

    # consents
    assert_consent(user.id, terms_consent_subject_id)
    assert_consent(user.id, privacy_policy_consent_subject_id)

    # newsletter subscription
    assert is_subscribed_to_brand_newsletter(user.id, brand.id)

    # confirmation e-mail

    verification_token = find_verification_token(user.id)
    assert verification_token is not None

    expected_sender = 'ACME Entertainment Convention <noreply@acmecon.test>'
    expected_recipients = ['hiro@metaverse.org']
    expected_subject = 'Hiro, bitte bestätige deine E-Mail-Adresse'
    expected_body = f"""
Hallo Hiro,

bitte bestätige deine E-Mail-Adresse hier:
https://www.acmecon.test/users/email_address/confirmation/{verification_token.token}
    """.strip()

    assert_email(
        send_email_mock,
        expected_sender,
        expected_recipients,
        expected_subject,
        expected_body,
    )


@patch('byceps.services.email.email_service.send')
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
        'first_name': 'Hiroaki',
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
    assert not is_subscribed_to_brand_newsletter(user.id, brand.id)


# helpers


def send_request(app, form_data):
    url = 'http://www.acmecon.test/users/'

    with http_client(app) as client:
        return client.post(url, data=form_data)


def find_user(screen_name):
    return user_service.find_db_user_by_screen_name(screen_name)


def get_user_count():
    return db.session.scalar(select(db.func.count(DbUser.id)))


def find_verification_token(user_id):
    return db.session.scalars(
        select(DbVerificationToken)
        .filter_by(user_id=user_id)
        .filter_by(_purpose=TokenPurpose.email_address_confirmation.name)
    ).first()


def is_subscribed_to_brand_newsletter(user_id, brand_id):
    return newsletter_service.is_user_subscribed_to_list(user_id, brand_id)


def assert_creation_log_entry_created(user_id, site_id):
    log_entries = user_log_service.get_entries_of_type_for_user(
        user_id, 'user-created'
    )
    assert len(log_entries) == 1

    first_log_entry = log_entries[0]
    assert first_log_entry.event_type == 'user-created'
    assert first_log_entry.data == {
        'creation_method': 'site app',
        'ip_address': '127.0.0.1',
        'site_id': site_id,
    }


def assert_password_credentials_created(user_id):
    credential = db.session.get(DbCredential, user_id)

    assert credential is not None
    assert credential.password_hash.startswith('scrypt:32768:8:1$')
    assert credential.updated_at is not None


def assert_consent(user_id, subject_id):
    assert consent_service.has_user_consented_to_subject(user_id, subject_id)


def assert_email(
    mock, expected_sender, expected_recipients, expected_subject, expected_body
):
    calls = mock.call_args_list
    assert len(calls) == 1

    pos_args, _ = calls[0]
    actual_sender, actual_recipients, actual_subject, actual_body = pos_args
    assert actual_sender == expected_sender
    assert actual_recipients == expected_recipients
    assert actual_subject == expected_subject
    assert actual_body == expected_body
