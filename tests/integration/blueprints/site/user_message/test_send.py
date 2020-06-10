"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.services.site import service as site_service

from tests.helpers import create_site, http_client, login_user


@pytest.fixture
def site1(admin_app, make_email_config):
    email_config = make_email_config(
        'acme-noreply',
        sender_address='noreply@acmecon.test',
        sender_name='ACME Entertainment Convention',
    )
    site = create_site(
        server_name='www.acmecon.test', email_config_id=email_config.id
    )
    yield site
    site_service.delete_site(site.id)


@pytest.fixture
def site2(admin_app, make_email_config):
    email_config = make_email_config(
        'acme-noreply-with-contact-address',
        sender_address='noreply@acmecon.test',
        sender_name='ACME Entertainment Convention',
        contact_address='help@acmecon.test',
    )
    site = create_site(
        server_name='www.acmecon.test', email_config_id=email_config.id
    )
    yield site
    site_service.delete_site(site.id)


@pytest.fixture(scope='module')
def user_alice(make_user):
    return make_user(
        'Alice',
        user_id='a4903d8f-0bc6-4af9-aeb9-d7534a0a22e8',
        email_address='alice@users.test',
    )


@pytest.fixture(scope='module')
def user_bob(make_user):
    return make_user(
        'Bob',
        user_id='11d72bab-3646-4199-b96c-e5e4c6f972bc',
        email_address='bob@users.test',
    )


@patch('byceps.email.send')
def test_send_when_logged_in_without_brand_contact_address(
    send_email_mock, party_app, site1, user_alice, user_bob
):
    sender = user_alice
    recipient = user_bob
    text = '''\
Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice
'''

    expected_response_location = f'http://www.acmecon.test/users/{recipient.id}'

    expected_email_sender = (
        'ACME Entertainment Convention <noreply@acmecon.test>'
    )
    expected_email_recipients = ['Bob <bob@users.test>']
    expected_email_subject = 'Mitteilung von Alice (über www.acmecon.test)'
    expected_email_body = '''\
Hallo Bob,

Alice möchte dir die folgende Mitteilung zukommen lassen.

Du kannst Alice hier antworten: http://www.acmecon.test/user_messages/to/a4903d8f-0bc6-4af9-aeb9-d7534a0a22e8/create

ACHTUNG: Antworte *nicht* auf diese E-Mail, sondern folge dem Link.

---8<-------------------------------------

Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice

---8<-------------------------------------

-- 
Diese Mitteilung wurde über die Website www.acmecon.test gesendet.\
'''

    response = send_request(
        party_app, recipient.id, text, current_user_id=sender.id
    )

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
    send_email_mock, party_app, site2, user_alice, user_bob,
):
    sender = user_bob
    recipient = user_alice
    text = '''\
Hey Alice,

nice to hear from you.

Best,
Bob
'''

    expected_response_location = f'http://www.acmecon.test/users/{recipient.id}'

    expected_email_sender = (
        'ACME Entertainment Convention <noreply@acmecon.test>'
    )
    expected_email_recipients = ['Alice <alice@users.test>']
    expected_email_subject = 'Mitteilung von Bob (über www.acmecon.test)'
    expected_email_body = '''\
Hallo Alice,

Bob möchte dir die folgende Mitteilung zukommen lassen.

Du kannst Bob hier antworten: http://www.acmecon.test/user_messages/to/11d72bab-3646-4199-b96c-e5e4c6f972bc/create

ACHTUNG: Antworte *nicht* auf diese E-Mail, sondern folge dem Link.

---8<-------------------------------------

Hey Alice,

nice to hear from you.

Best,
Bob

---8<-------------------------------------

-- 
Diese Mitteilung wurde über die Website www.acmecon.test gesendet.
Bei Fragen kontaktiere uns bitte per E-Mail an: help@acmecon.test\
'''

    response = send_request(
        party_app, recipient.id, text, current_user_id=sender.id
    )

    assert response.status_code == 302
    assert response.location == expected_response_location

    send_email_mock.assert_called_once_with(
        expected_email_sender,
        expected_email_recipients,
        expected_email_subject,
        expected_email_body,
    )


def test_send_when_not_logged_in(party_app, site1):
    recipient_id = '8e5037f6-3ca1-4981-b1e4-1998cbdf58e2'
    text = 'Hello, Eve!'

    response = send_request(party_app, recipient_id, text)

    assert response.status_code == 302
    assert response.location == 'http://www.acmecon.test/authentication/login'


# helpers


def send_request(app, recipient_id, text, *, current_user_id=None):
    url = f'/user_messages/to/{recipient_id}/create'

    form_data = {'body': text}

    if current_user_id is not None:
        login_user(current_user_id)

    with http_client(app, user_id=current_user_id) as client:
        return client.post(url, data=form_data)
