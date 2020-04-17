"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.services.site import service as site_service

from tests.conftest import database_recreated
from tests.helpers import create_site, create_user, http_client, login_user


@pytest.fixture(scope='module')
def app(party_app, db, make_email_config):
    with party_app.app_context():
        with database_recreated(db):
            make_email_config(
                sender_address='noreply@example.com',
                sender_name='ACME Entertainment Convention',
            )
            yield party_app


@pytest.fixture(scope='module')
def site(app):
    site = create_site(server_name='acme.example.com')
    yield site
    site_service.delete_site(site.id)


@pytest.fixture(scope='module')
def user_alice(app):
    return create_user(
        'Alice',
        user_id='a4903d8f-0bc6-4af9-aeb9-d7534a0a22e8',
        email_address='alice@example.com',
    )


@pytest.fixture(scope='module')
def user_bob(app):
    return create_user(
        'Bob',
        user_id='11d72bab-3646-4199-b96c-e5e4c6f972bc',
        email_address='bob@example.com',
    )


@patch('byceps.email.send')
def test_send_when_logged_in_without_brand_contact_address(
    send_email_mock, app, site, user_alice, user_bob
):
    sender = user_alice
    recipient = user_bob
    text = '''\
Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice
'''

    expected_response_location = f'http://example.com/users/{recipient.id}'

    expected_email_sender = (
        'ACME Entertainment Convention <noreply@example.com>'
    )
    expected_email_recipients = ['Bob <bob@example.com>']
    expected_email_subject = 'Mitteilung von Alice (über acme.example.com)'
    expected_email_body = '''\
Hallo Bob,

Alice möchte dir die folgende Mitteilung zukommen lassen.

Du kannst Alice hier antworten: http://example.com/user_messages/to/a4903d8f-0bc6-4af9-aeb9-d7534a0a22e8/create

ACHTUNG: Antworte *nicht* auf diese E-Mail, sondern folge dem Link.

---8<-------------------------------------

Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice

---8<-------------------------------------

-- 
Diese Mitteilung wurde über die Website acme.example.com gesendet.\
'''

    response = send_request(app, recipient.id, text, current_user_id=sender.id)

    assert response.status_code == 302
    assert response.location == expected_response_location

    send_email_mock.assert_called_once_with(
        expected_email_sender,
        expected_email_recipients,
        expected_email_subject,
        expected_email_body,
    )


@patch('byceps.email.send')
def test_send_when_logged_in_with_brand_contact_address(
    send_email_mock, app, make_email_config, site, user_alice, user_bob
):
    make_email_config(
        sender_address='noreply@example.com',
        sender_name='ACME Entertainment Convention',
        contact_address='help@example.com',
    )

    sender = user_bob
    recipient = user_alice
    text = '''\
Hey Alice,

nice to hear from you.

Best,
Bob
'''

    expected_response_location = f'http://example.com/users/{recipient.id}'

    expected_email_sender = (
        'ACME Entertainment Convention <noreply@example.com>'
    )
    expected_email_recipients = ['Alice <alice@example.com>']
    expected_email_subject = 'Mitteilung von Bob (über acme.example.com)'
    expected_email_body = '''\
Hallo Alice,

Bob möchte dir die folgende Mitteilung zukommen lassen.

Du kannst Bob hier antworten: http://example.com/user_messages/to/11d72bab-3646-4199-b96c-e5e4c6f972bc/create

ACHTUNG: Antworte *nicht* auf diese E-Mail, sondern folge dem Link.

---8<-------------------------------------

Hey Alice,

nice to hear from you.

Best,
Bob

---8<-------------------------------------

-- 
Diese Mitteilung wurde über die Website acme.example.com gesendet.
Bei Fragen kontaktiere uns bitte per E-Mail an: help@example.com\
'''

    response = send_request(app, recipient.id, text, current_user_id=sender.id)

    assert response.status_code == 302
    assert response.location == expected_response_location

    send_email_mock.assert_called_once_with(
        expected_email_sender,
        expected_email_recipients,
        expected_email_subject,
        expected_email_body,
    )


def test_send_when_not_logged_in(app, site):
    recipient_id = '8e5037f6-3ca1-4981-b1e4-1998cbdf58e2'
    text = 'Hello, Eve!'

    response = send_request(app, recipient_id, text)

    assert response.status_code == 302
    assert response.location == 'http://example.com/authentication/login'


# helpers


def send_request(app, recipient_id, text, *, current_user_id=None):
    url = f'/user_messages/to/{recipient_id}/create'

    form_data = {'body': text}

    if current_user_id is not None:
        login_user(current_user_id)

    with http_client(app, user_id=current_user_id) as client:
        return client.post(url, data=form_data)
